import streamlit as st
import pandas as pd
import pycountry as py
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title = "Dashboard da quantidade de pessoas na academia",
    page_icon = "📊",
    layout = "wide"
)

# --- Carregamento dos Dados ---
df = pd.read_csv("Analise_Dados.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔎 Filtros")

# Filtro Gênero
genero_disponiveis = sorted(df["Genêro"].unique())
genero_selecionados = st.sidebar.multiselect("Genêro", genero_disponiveis, default = genero_disponiveis)

# Filtro Tipo de Treino
tipo_treino_disponiveis = sorted(df["Tipo_Treino"].unique())
tipo_treino_selecionados = st.sidebar.multiselect("Tipo de Treino", tipo_treino_disponiveis, default = tipo_treino_disponiveis)

# Filtro de presença
presença_disponivel = sorted(df["Status_Presença"].unique())
presença_selecionada = st.sidebar.multiselect("Presença", presença_disponivel, default = presença_disponivel)

# Filtro Idade
idade_disponivel = sorted(df["Idade"].unique())
idade_selecionada = st.sidebar.multiselect("Idade", idade_disponivel, default = idade_disponivel)

# Filtro do DataFrame
#Serve para que todas as alterações nos filtros também apareçam no escopo e no grafico de todo o site
df_filtrado = df[
    (df["Genêro"].isin(genero_selecionados)) &
    (df["Tipo_Treino"].isin(tipo_treino_selecionados)) &
    (df["Status_Presença"].isin(presença_selecionada)) &
    (df["Idade"].isin(idade_selecionada))
]

# --- Conteúdo Principal ---
st.title("Dashboard da quantidade de pessoas na academia de acordo com certos fatores")
st.markdown("Exploque a quantidade de pessoas nos ultimos anos. Utilize os filtros à esquerda para refinar sua pesquisa")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")
if not df_filtrado.empty:
    genero_geral = df_filtrado["Genêro"].mode()[0]
    idade_geral = df_filtrado["Idade"].mode()[0]
    treino_geral = df_filtrado["Tipo_Treino"].mode()[0]
else:
    genero_geral, idade_geral, treino_geral = ""

col1, col2, col3 = st.columns(3)
col1.metric("Gênero mais frequente", genero_geral)
col2.metric("Idade mais frequente", idade_geral)
col3.metric("Treino mais frequente", treino_geral)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

#Criando váriaveis que ligam as colunas com os gráficos
col_graf1, col_graf2 = st.columns(2)
col_graf3, col_graf4 = st.columns(2)

#Gráfico de Gêneros
with col_graf1:
    if not df_filtrado.empty:
        genero_contagem = df_filtrado["Genêro"].value_counts().reset_index()
        genero_contagem.columns = ["Tipo de Gênero", "Quantidade"]

        graf_piz = px.pie(
            genero_contagem,
            names = "Tipo de Gênero",
            values = "Quantidade",
            hole = 0.5
        )
        graf_piz.update_traces(textinfo = "percent + label")
        st.plotly_chart(graf_piz, use_container_width = True)
    else:
        st.warning("Nenhum dado para exibir no Gráfico de Gêneros")
#Gráfico de idades
with col_graf2:
    if not df_filtrado.empty:
        idade_contada = df_filtrado["Idade"].value_counts().reset_index()
        idade_contada.columns = ["Idade", "Quantidade"]

        graf_bar = px.bar(
            idade_contada,
            x = "Idade",
            y = "Quantidade",
            labels = {"quantidade" : "Somatório das pessoas que nasceram no mesmo ano"},
            title = "Idade dentro da Academia"
        )
        graf_bar.update_traces(texttemplate = "%{y}", textangle = 0)
        st.plotly_chart(graf_bar, use_container_width = True)
    else:
        st.warning("Nenhum dado para exibir no Gráfico de idades")
#Gráfico do tipo de treino e pessoas
with col_graf3:
    if not df_filtrado.empty:
        treino_contagem = df_filtrado["Tipo_Treino"].value_counts().reset_index()
        treino_contagem.columns = ["Tipo de Treino", "Quantidade de Pessoas"]

        graf_his = px.histogram(
            treino_contagem,
            x = "Tipo de Treino",
            y = "Quantidade de Pessoas",
            title = "Modalidades de Treino na Academia"
        )
        graf_his.update_traces(texttemplate = "%{y}" , textangle = 0)
        st.plotly_chart(graf_his, use_container_width = True)
    else:
        st.warning("Nenhum dado para mostrar em Modalidade de Treino na Academia")

#Gráfico de Presença
with col_graf4:
    if not df_filtrado.empty:
        presença_contagem = df_filtrado["Status_Presença"].value_counts().reset_index()
        presença_contagem.columns = ["Presença", "Quantidade"]

        graf_piz2 = px.pie(
            presença_contagem,
            names = "Presença",
            values = "Quantidade",
            hole = 0.5
)
        graf_piz2.update_traces(textinfo = "percent + label")
        st.plotly_chart(graf_piz2, use_container_width = True)
    else:
        st.warning("Nenhum dado para mostrar no gráfico de presença")

#--- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)