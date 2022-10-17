import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pycaret.classification import load_model, predict_model

# Nome e ícone que aparecerá na aba.
st.set_page_config(page_title="Modelo de Churn", page_icon="📊")

# Carregando os arquivos.
model = load_model("datalake/curated/model")
model_cluster = joblib.load("datalake/curated/cluster.joblib")
dataset = pd.read_csv("datalake/curated/dataset.csv")

# Título
st.title("Human Resource Analytics")

st.markdown(
    """<p style="font-family:Cambria; font-size: 20px; text-align: justify">Esse projeto foi feito para resolver um problema comum na área de <i>Human Resources</i> (ou RH em português) chamado de <i>Churn</i>, ou mais espeficamente <i>Churn Rate</i>. O <i>Churn Rate</i> é taxa com a qual um número de pessoas ou objetos saem de um grupo. Aplicando esse conceito ao âmbito empresarial, temos que o <i>Churn Rate</i> se aplica à taxa com que funcionários são demitidos, e a isso está associado todo o custo de a empresa perder alguém com uma função chave, ter que operar com menor capacidade, além de refazer o processo seletivo. Tudo isso despende tempo e dinheiro, e é visando evitar isso que fizemos essa aplicação. <br><br> No menu abaixo você pode escolher alguns atributos associados ao colaborador da empresa, e então o modelo de <i>Machine Learning</i> irá prever a probabilidade desse funcionário pedir demissão. Perceba que se o modelo previr uma alta taxa de evasão, o recomendado será entrar em contato com esse colaborador para melhorarmos a relação entre ele e a empresa, tentando impedir a rotatividade de funcionários. O gráfico abaixo mostra os três principais grupos de empregados que saíram da empresa, os eixos do gráfico são a nota que a empresa deu a eles e quais foram as suas notas de satisfação em relação à empresa antes de deixá-la. O empregado avaliado aparecerá como um ponto amarelo no gráfico. Perceba que estamos considerando outras duas características que não aparecem no gráfico, as horas trabalhadas e o tempo na empresa, então, se o empregado aparecer dentro de algum grupo não necessariamente ele terá chances altas de sair.</p>""",
    unsafe_allow_html=True,
)

"---"

# Clusters de empregados que pediram demissão.
kmeans_colors = [
    "red" if c == 0 else "blue" if c == 1 else "green" for c in model_cluster.labels_
]

col_1, col_2, col_3, col_4 = st.columns(4)

# Mapeando dados do usuário para cada atributo.
satisfaction = col_1.number_input(
    "Satisfação do empregado", min_value=0.0, max_value=100.0, value=50.0, step=0.5
)
evaluation = col_2.number_input(
    "Nota dada ao empregado", min_value=0.0, max_value=100.0, value=50.0, step=0.5
)
averageMonthlyHours = col_3.number_input(
    "Horas trabalhadas", min_value=0, step=1, value=250, help="Nos últimos 3 meses!"
)
yearsAtCompany = col_4.number_input(
    "Anos na empresa", min_value=0.0, step=0.5, value=3.0
)

# Criando instância de funcionário.
instance = pd.DataFrame(
    [[satisfaction, evaluation, averageMonthlyHours, yearsAtCompany]]
)
instance.columns = [
    "satisfaction",
    "evaluation",
    "averageMonthlyHours",
    "yearsAtCompany",
]

# Fazendo a predição.
result = predict_model(model, data=instance)

# Classe e probabilidade previstas.
classe = result["Label"][0]
prob = result["Score"][0] * 100

# Plotagem interativa dos clusters.
fig = px.scatter(
    dataset[dataset.turnover == 1],
    x="satisfaction",
    y="evaluation",
    color=kmeans_colors,
)

# Definindo título, rótulo, tamanho da fonte e escondendo a legenda.
fig.update_layout(
    title="Satisfação vs Nota do Empregado",
    xaxis_title="Satisfação",
    yaxis_title="Nota do Empregado",
    font=dict(size=15),
    showlegend=False,
)

# Definindo a descrição quando se passa o mouse sobre algum dado.
fig.update_traces(hovertemplate="Nota do Empregado: %{y} <br>Satisfação: %{x}")

# Adicionando o ponto associado ao empregado
fig.add_trace(
    go.Scattergl(
        x=[satisfaction],
        y=[evaluation],
        mode="markers",
        marker=dict(size=[10], color=["yellow"]),
        name="Empregado",
    )
)

# Mostrando a plotagem.
st.plotly_chart(fig)

# Mostrando o valor da predição.
if classe == 1:
    st.markdown(
        f"""<p style="font-family:Cambria; font-size: 23px; text-align: center">Predição do modelo: <b>Evasão</b> com probabilidade de <b>{prob:.2f}%</b></p>""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""<p style="font-family:Cambria; font-size: 23px; text-align: center">Predição do modelo: <b>Permanência</b> com probabilidade de <b>{prob:.2f}%</b></p>""",
        unsafe_allow_html=True,
    )

"---"

# Logo do Github.
st.markdown(
    """<p style="text-align: center;"><a style="text -decoration> none" href="https://github.com/joao-vitor-souza/bootcamp-stack-2021"><img src="https://i.ibb.co/PYvPb4r/imagem-menu.png" alt="Github" width="220" height="82"></a></p>""",
    unsafe_allow_html=True,
)
