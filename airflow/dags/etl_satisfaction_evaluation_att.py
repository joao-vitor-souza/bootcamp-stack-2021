from datetime import datetime

import pandas as pd
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from minio import Minio

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
    "etl_satisfaction_evaluation_att",  # Nome da DAG.
    default_args=DEFAULT_ARGS,  # Passando os argumentos.
    schedule_interval="@once",  # O Airflow Scheduler só executará a DAG uma única vez.
)

# Variáveis de ambiente do datalake.
data_lake_server = Variable.get("data_lake_server")  # IP do datalake.
data_lake_login = Variable.get("data_lake_login")  # Usuário.
data_lake_password = Variable.get("data_lake_password")  # Senha.

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

    # Recuperando o arquivo a partir do datalake.
    obj = client.get_object(
        "landing",  # Nome do bucket.
        "performance-evaluation/employee_performance_evaluation.json",  # Caminho do arquivo.
    )

    # Leitura do arquivo.
    data = obj.read()
    df_ = pd.read_json(data, lines=True)

    # Persistindo os dados temporariamente.
    df_.to_json(
        "/tmp/employee_performance_evaluation.json", orient="records", lines=True
    )


# L: Load
def load():

    # Lendo os arquivos temporários.
    df_ = pd.read_json(
        "/tmp/employee_performance_evaluation.json", orient="records", lines="True"
    )

    # Convertendo os dados para o formato parquet.
    df_[["satisfaction_level", "last_evaluation"]].to_parquet(
        "/tmp/satisfaction_evaluation.parquet", index=False
    )

    # Enviando os dados para o bucket processing do datalake.
    client.fput_object(
        "processing",  # Nome do bucket.
        "satisfaction_evaluation.parquet",  # Nome do arquivo no bucket.
        "/tmp/satisfaction_evaluation.parquet",  # Caminho atual do arquivo no datalake.
    )


# Operadores Python.
extract_task = PythonOperator(
    task_id="extract_file_from_data_lake",  # Nome da tarefa.
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
    # Comando para remover (rm) todos os arquivos (-f) temporários do tipo .csv, .json e .parquet do datalake.
    bash_command="rm -f /tmp/*.csv;rm -f /tmp/*.json;rm -f /tmp/*.parquet;",
    dag=dag,
)

# Ordem da execução das tarefas.
extract_task >> load_task >> clean_task
