![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Heroku](https://img.shields.io/badge/heroku-%23430098.svg?style=for-the-badge&logo=heroku&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)


<img src="https://img.shields.io/github/issues-raw/joao-vitor-souza/Human-Resource-Analytics-Bootcamp-Stack-2021?style=flat-square"> <img src="https://img.shields.io/github/license/joao-vitor-souza/Human-Resource-Analytics-Bootcamp-Stack-2021?style=flat-square"> <img src="https://img.shields.io/github/languages/count/joao-vitor-souza/Human-Resource-Analytics-Bootcamp-Stack-2021?style=flat-square">
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

<img src="https://media-exp1.licdn.com/dms/image/C4D0BAQF26jZ3QdJQcg/company-logo_200_200/0/1624621563131?e=2147483647&v=beta&t=_ZCPRmKX4seKsn2lNkJ3GZI52xIPpE07_iOVZcv7xR4" width=130px height=130px align="right">

# Bootcamp DS 2021 da [Stack Tecnologias](https://www.youtube.com/c/Stack_tecnologias)
<br>

<div align='justify'>

### Seja muito bem vindo! 

  >Esse projeto é baseado no Bootcamp realizado pela Stack Tecnologias no final do ano de 2021. Nele partimos dos dados estruturados no banco de dados MySQL da empresa e dos mais diversos dados espalhados pelos seus setores, agrupamos tudo que temos em um Data Lake MinIO, usamos funções de ETL com as DAGs do Airflow, fazemos análises descritivas dos dados, treinamos diversos modelos de predição e usamos a biblioteca de Auto-ML Pycaret.
  >
  >Mas afinal, do que se trata essa aplicação? Qual o problema que estamos resolvendo para a empresa?
  >
  >Pois bem, todo esse projeto foi voltado para um problema comum na área de Human Resources (ou RH em português) chamado de Churn, ou mais espeficamente Churn Rate. O Churn Rate é taxa com a qual um número de pessoas ou objetos saem de um grupo. Aplicando esse conceito ao âmbito empresarial, temos que o Churn Rate se aplica à taxa com que funcionários são demitidos, e a isso está associado todo o custo de a empresa perder alguém com uma função chave, ter que operar com menor capacidade, além de refazer o processo seletivo. Tudo isso despende tempo e dinheiro, e é visando evitar isso que fizemos essa aplicação. 
  >
  >Mas como fazemos isso? Basicamente usaremos dados já disponíveis para treinar modelos de aprendizado de máquina e descobriremos padrões entre aqueles funcionários que se demitiram, assim poderemos prever quais funcionários têm alta probabilidade de deixar a empresa, e com isso faremos contato visando melhorar a relação entre eles e a empresa. 
  >
  >Em seguida explicarei como você pode clonar esse repositório para sua máquina local e criar os servidores locais necessários usando o Docker.

---
### - Clonando este repositório

  >Já supondo que você tenha o GIT instalado (caso não, faça o [download](https://git-scm.com/downloads)), então abra o seu terminal, caminhe até o diretório que queira fazer o clone e digite:

```
git clone https://github.com/joao-vitor-souza/bootcamp-stack-2021
```

---
### - Criando os contêineres
  
  >Como já foi falado, usaremos um banco de dados MySQL, um Data Lake MinIO e um servidor para o orquestrador de tarefas Airflow. Para sistematizar, permitir reproducilibidade e garantir interoperabilidade, criaremos todos os três usando imagens disponíveis no Docker Hub. Caso precise instalar o Docker na sua máquina, clique [aqui](https://www.docker.com/get-started/). Começaremos com o banco de dados, para isso abra o seu terminal e digite o seguinte comando:
  
```
docker run --name mysqlbd1 -e MYSQL_ROOT_PASSWORD=bootcamp -p "3307:3306" -d mysql
```
  
  - `--name`: Define o <b>nome</b> do contêiner;
  - `-e`    : Declara variáveis de ambiente (<b>e</b>nviroment variables);
  - `-p`    : Faz o mapeamento de <b>p</b>ortas;
  - `-d`    : Roda o contêiner de forma <b>d</b>esatachada, isto é, em segundo plano. Isso permite que usemos o terminal e o contêiner ao mesmo tempo.

  >Esse comando chamará o utilitário do `docker` no modo de criação `run`, então passamos o nome do contêiner `mysqldb1`, definimos a senha do banco `MYSQL_ROOT_PASSWORD=bootcamp` e fazemos o mapeamento de portas entre nossa máquina local e o contêiner `"3307:3306"`, no final passamos a imagem que estamos usando, `mysql`. Em seguida, criaremos o Data Lake:
  
  ```
  docker run --name minio -d -p 9000:9000 -p 9001:9001 -v "$PWD/datalake:/data" minio/minio server /data --console-address ":9001"
  ```
  
  - `-v`: Estabelece a persistência de arquivos, criando um <b>v</b>olume;
  - `--console-adress`: Expõe a porta `:9001`do console.
  
  >Usando a imagem `minio/minio` criamos um Data Lake MinIO. Dessa vez mapeamos duas portas, `9000` e `9001`. Além disso criamos um volume de dados localmente. Isso significa dizer que tudo que for colocado no diretório `/data` do contêiner será copiado para `$PWD/datalake` na nossa máquina (`$PWD = Print Working Directory`) e vice-versa. Isso permite que persistamos os dados, <b>se não fizermos isso tudo será perdido quando desligarmos o contêiner</b>. Por último, e um pouco mais complicado, está o Airflow:
  
  ```
  docker run -d -p 8080:8080 -v "$PWD/airflow/dags:/opt/airflow/dags/" --entrypoint=/bin/bash --name airflow apache/airflow:2.1.1-python3.8 -c '(airflow db init && airflow users create --username admin --password admin --firstname admin --lastname admin --role Admin --email admin@example.org); airflow webserver & airflow scheduler'
  ```
  
  - `--entrypoint`: Código que será executado sempre que a imagem for chamada. No caso, o código `/bin/bash` abrirá o GNU Bash;
  - `-c`: Define os <b>c</b>omandos que serão executados dentro do GNU.
  
  >Uma vez criado o Airflow, entramos no seu terminal por meio do Bash e então iniciamos o seu banco de dados `airflow db init`, o UI webserver `airflow webserver` e o agendador de tarefas `airflow scheduler`. As credenciais do usuário são todas definidas através das tags do comando `airflow users create`.
  >
  >Depois de os três servidores terem sido criados, inicie-os caso estejam desligados:
  
  ```
  docker start mysqldb1 airflow minio
  ```
  
  >Agora você precisará verificar a conexão com o banco de dados, criar os buckets do MinIO e definir as variáveis de ambiente do Airflow, tudo está explicado passo a passo no PDF da Aula 02 na pasta `pdf_aulas`.

  ---
  
  ### Referências externas:

  >DataApp: https://predicao-churn.herokuapp.com/
  >
  >[Linkedin](https://br.linkedin.com/company/stack-tecnologias) da Stack Tecnologias.
  >
  >Canal da Stack no [Youtube](https://www.youtube.com/c/Stack_tecnologias).

</div>
