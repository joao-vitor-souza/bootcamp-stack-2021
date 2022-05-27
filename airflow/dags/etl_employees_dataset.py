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
    "etl_employees_dataset",  # Nome da DAG.
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

    # Cria um dataframe vazio.
    df = pd.DataFrame(data=None)

    objects = client.list_objects(
        "processing",  # Busca os arquivos no bucket processing do datalake.
        recursive=True,  # Todos os arquivos serão buscados recursivamente.
    )

    # Iterando cada objeto.
    for obj in objects:

        client.fget_object(
            obj.bucket_name,  # Nome do bucket.
            obj.object_name.encode("utf-8"),  # Nome do arquivo.
            "/tmp/temp_.parquet",  # Local que arquivo será salvo temporariamente no formato parquet.
        )

        # Lendo o arquivo em um dataframe e concatenando.
        df_temp = pd.read_parquet("/tmp/temp_.parquet")
        df = pd.concat([df, df_temp], axis=1)

    # Persistindo os dados temporariamente.
    df.to_csv("/tmp/employees_dataset.csv", index=False)


# L: Load
def load():

    # Carregando os dados temporários.
    df_ = pd.read_csv("/tmp/employees_dataset.csv")

    # Convertendo os dados para o formato parquet.
    df_.to_parquet("/tmp/employees_dataset.parquet", index=False)

    # Enviando os dados para o bucket processing do datalake.
    client.fput_object(
        "processing",  # Nome do bucket.
        "employees_dataset.parquet",  # Nome do arquivo no bucket.
        "/tmp/employees_dataset.parquet",  # Caminho do arquivo.
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
