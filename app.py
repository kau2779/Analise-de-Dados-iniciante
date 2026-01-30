import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title = "Dashboard de Salários na Área de Dados",
    page_icon = "📊",
    layout = "wide"
)

# --- Carregamento dos Dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv") #df == DataFrame

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df["ano"].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default= anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df["senioridade"].unique())
senioridades_selecionada = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default = senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df["contrato"].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default = contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df["tamanho_empresa"].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default = tamanhos_disponiveis)

# Filtro por Tipo de Trabalho
trabalhos_disponiveis = sorted(df["remoto"].unique())
trabalhos_selecionados = st.sidebar.multiselect("Modelo de Trabalho", trabalhos_disponiveis, default = trabalhos_disponiveis)

# Filtro do DataFrame
#Serve para que todas as alterações nos filtros também apareçam no escopo e no grafico de todo o site
df_filtrado = df[
    (df["ano"].isin(anos_selecionados)) &
    (df["senioridade"].isin(senioridades_selecionada)) &
    (df["contrato"].isin(contratos_selecionados)) &
    (df["tamanho_empresa"].isin(tamanhos_selecionados)) &
    (df["remoto"].isin(trabalhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
    modelo_trabalho = df_filtrado["remoto"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum, modelo_normal = 0, 0, 0, ""

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)
col5.metric("Modelo de Trabalho", modelo_trabalho)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gáficos")

#Criando váriaveis que ligam as colunas com os gráficos
col_graf1, col_graf2 = st.columns(2)
col_graf3, col_graf4 = st.columns(2)
col_graf5 = st.columns(1)

#Gráfico de Cargos
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby("cargo")["usd"].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(top_cargos,
            x ='usd',
            y ='cargo',
            orientation ='h',
            title ="Top 10 cargos por salário médio",
            labels ={'usd': 'Média salarial anual (USD)', 'cargo': ''})
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width = True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

#Gráfico de Distribuição
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x = "usd",
            nbins = 30,
            title = "Distribuição de salários anuais",
            labels = {"usd" : "Faixa salarial (USD)", "count" : ""}
        )
        grafico_hist.update_layout(title_x = 0.1)
        st.plotly_chart(grafico_hist, use_container_width = True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

#Gráfico Modo de Trabalho
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado["remoto"].value_counts().reset_index()
        remoto_contagem.columns = ["tipo_trabalho" , "quantidade"]
        grafico_remoto = px.pie(
            remoto_contagem,
            names = "tipo_trabalho",
            values = "quantidade",
            title = "Proporção dos tipos de trabalho",
            hole = 0.5
        )
        grafico_remoto.update_traces(textinfo = "percent + label")
        grafico_remoto.update_layout(title_x = 0.1)
        st.plotly_chart(grafico_remoto, use_container_width = True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

#Gráfico da Quantidade de Renda dos trabalhadores de cada país
with col_graf4:
    if not df_filtrado.empty:
        # Função para converter ISO-2 para ISO-3
        def iso2_to_iso3(iso2_code):
            try:
                return pycountry.countries.get(alpha_2=iso2_code).alpha_3
            except:
                return None

        # Prepara os dados
        df_ds = df_filtrado[df_filtrado["cargo"] == "Data Scientist"]
        media_ds_ps = df_ds.groupby("residencia")["usd"].mean().reset_index()
        media_ds_ps["residencia"] = media_ds_ps["residencia"].apply(iso2_to_iso3)
        media_ds_ps = media_ds_ps.dropna(subset=["residencia"])
        # Cria o mapa
        grafico_paises = px.choropleth(
            media_ds_ps,
            locations="residencia",
            locationmode="ISO-3",
            color="usd",
            color_continuous_scale="Viridis",  # Mudei a escala
            hover_name="residencia",  # Mostra o nome ao passar o mouse
            hover_data={"usd": True, "residencia": False},  # Customiza o hover
            title="Distribuição de Profissionais por País de Residência",
            labels={"usd": "Salário Médio (USD)"},  # Label melhor
            height=700,
            width=1000
        )

        # Ajusta o layout
        grafico_paises.update_geos(
            showcoastlines=True,
            showland=True,
            landcolor="lightgray",
            projection_type="natural earth"  # Projeção mais bonita
        )

        grafico_paises.update_layout(
            title_x = 0.1,
            margin={"r":0,"t":50,"l":0,"b":0},
            geo=dict(showframe=False, showcoastlines=True)
        )
        st.plotly_chart(grafico_paises, use_container_width = True)
    else:
         st.warning("Nenhum dado para exibir no gráfico de países.")

#--- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)