from datetime import datetime

import pandas as pd
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from minio import Minio
from sqlalchemy.engine import create_engine

from airflow import DAG

# Argumentos da DAG.
DEFAULT_ARGS = {
    "owner": "Airflow",  # Nome de usuário.
    "depends_on_past": False,  # A DAG não dependerá informações passadas.
    "start_date": datetime(
        2021, 1, 13
    ),  # Data de início (atrasada) da execução da DAG.
}

# Instanciando a DAG.
dag = DAG(
    "etl_department_salary_left_att",  # Nome da DAG.
    default_args=DEFAULT_ARGS,  # Passando os argumentos.
    schedule_interval="@once",  # O Airflow Scheduler só executará a DAG uma única vez.
)

# Variáveis de ambiente do datalake.
data_lake_server = Variable.get("data_lake_server")  # IP do datalake.
data_lake_login = Variable.get("data_lake_login")  # Usuário.
data_lake_password = Variable.get("data_lake_password")  # Senha.

# Variáveis de ambiente do banco de dados.
database_server = Variable.get("database_server")  # IP do banco de dados.
database_login = Variable.get("database_login")  # Usuário.
database_password = Variable.get("database_password")  # Senha.
database_name = Variable.get("database_name")  # Nome do banco.

# Criando conexão com o banco.
connection = "mysql+pymysql://{}:{}@{}/{}".format(
    str(database_login),
    str(database_password),
    str(database_server),
    str(database_name),
)

engine = create_engine(connection)

# Criando objeto client do datalake com as variáveis de ambiente já definidas.
client = Minio(
    data_lake_server,
    access_key=data_lake_login,
    secret_key=data_lake_password,
    secure=False,
)

# Funções ETL

# E: Extract
def extract():

    # Query para consultar tabelas múltiplas no banco de dados.
    query = """SELECT emp.department as department, sal.salary as salary, emp.left
            FROM employees emp
            INNER JOIN salaries sal
            ON emp.emp_no = sal.emp_id;"""

    # Consultando e retornando para um dataframe.
    df_ = pd.read_sql_query(query, engine)

    # Persistindo os dados temporariamente.
    df_.to_csv("/tmp/department_salary_left.csv", index=False)


# L: Load
def load():

    # Carregando os dados temporários.
    df_ = pd.read_csv("/tmp/department_salary_left.csv")

    # Convertendo os dados para o formato parquet.
    df_.to_parquet("/tmp/department_salary_left.parquet", index=False)

    # Enviando os dados para o bucket processing do datalake.
    client.fput_object(
        "processing",  # Nome do bucket.
        "department_salary_left.parquet",  # Nome do arquivo no bucket.
        "/tmp/department_salary_left.parquet",  # Caminho atual do arquivo no datalake.
    )


# Operadores Python.
extract_task = PythonOperator(
    task_id="extract_data_from_database",  # Nome da tarefa.
    provide_context=True,  # Permite que as variáveis de contexto do Airflow sejam passadas para o operador
    python_callable=extract,  # Nome da função.
    dag=dag,  # DAG que receberá o operador.
)

load_task = PythonOperator(
    task_id="load_file_to_data_lake",
    provide_context=True,
    python_callable=load,
    dag=dag,
)

# Operador Bash.
clean_task = BashOperator(
    task_id="clean_files_on_staging",
    dag=dag,
    # Comando para remover (rm) todos os arquivos (-f) temporários do tipo .csv, .json e .parquet do datalake.
    bash_command="rm -f /tmp/*.csv;rm -f /tmp/*.json;rm -f /tmp/*.parquet;",
)

# Ordem da execução das tarefas.
extract_task >> load_task >> clean_task
