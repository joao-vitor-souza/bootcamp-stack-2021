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
    "etl_mean_work_last_3_months_att",  # Nome da DAG.
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

    # Cria um dataframe vazio com colunas já nomeadas.
    df_working_hours = pd.DataFrame(data=None, columns=["emp_id", "data", "hora"])

    objects = client.list_objects(
        "landing",  # Busca os arquivos no bucket landing do datalake.
        prefix="working-hours",  # Prefixo do diretório no bucket.
        recursive=True,  # Buscando recursivamente por todos os arquivos no diretório.
    )

    # Iterando cada objeto.
    for obj in objects:

        obj = client.get_object(
            obj.bucket_name,  # Nome do bucket.
            obj.object_name.encode("utf-8"),  # Nome do arquivo.
        )

        # Lendo o arquivo xlsx.
        data = obj.read()
        df_ = pd.read_excel(data)

        # Concatenando.
        df_working_hours = pd.concat([df_working_hours, df_])

    # Persistindo os dados temporariamente.
    df_working_hours.to_csv("/tmp/mean_work_last_3_months.csv", index=False)


# T: Transform
def transform():

    # Lendo os arquivos temporários.
    df_ = pd.read_csv("/tmp/mean_work_last_3_months.csv")

    # Convertendo o atributo hora e data para numérico e datetime, respectivamente.
    df_["hora"] = pd.to_numeric(df_["hora"])
    df_["data"] = pd.to_datetime(df_["data"])

    # Filtrando apenas os registros dos últimos 3 meses. A referência é o final do ano de 2020.
    df_last_3_month = df_[(df_["data"] > datetime(2020, 9, 30))]

    # Calculando as horas de trabalho média nos últimos 3 meses.
    mean_work_last_3_months = df_last_3_month.groupby("emp_id")["hora"].sum() / 3

    # Dataframe com os dados transformados.
    mean_work_last_3_months = pd.DataFrame(data=mean_work_last_3_months)
    mean_work_last_3_months.rename(
        columns={"hora": "mean_work_last_3_months"}, inplace=True
    )

    # Persistindo os dados temporariamente.
    mean_work_last_3_months.to_csv("/tmp/mean_work_last_3_months.csv", index=False)


# L: Load
def load():

    # Lendo os arquivos temporários.
    df_ = pd.read_csv("/tmp/mean_work_last_3_months.csv")

    # Convertendo os dados para o formato parquet.
    df_.to_parquet("/tmp/mean_work_last_3_months.parquet", index=False)

    # Enviando os dados para o bucket processing do datalake.
    client.fput_object(
        "processing",  # Nome do bucket.
        "mean_work_last_3_months.parquet",  # Nome do arquivo no bucket.
        "/tmp/mean_work_last_3_months.parquet",  # Caminho atual do arquivo no datalake.
    )


# Operadores Python.
extract_task = PythonOperator(
    task_id="extract_file_from_data_lake",  # Nome da tarefa.
    provide_context=True,  # Permite que as variáveis de contexto do Airflow sejam passadas para o operador
    python_callable=extract,  # Nome da função.
    dag=dag,  # DAG que receberá o operador.
)

transform_task = PythonOperator(
    task_id="transform_data", provide_context=True, python_callable=transform, dag=dag
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
extract_task >> transform_task >> load_task >> clean_task
