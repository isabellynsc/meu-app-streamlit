import streamlit as st
import pandas as pd
from io import BytesIO

# ✅ CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Comparador de Contratos",
    page_icon="📊",
    layout="centered"
)

# ✅ LOGO (PROTEGIDA PRA NÃO QUEBRAR)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.JPG", width=200)
    except:
        st.write("")  # evita erro se a logo não estiver disponível

# ✅ TÍTULO CORRETO (HTML SEM ERRO)
st.markdown(
    "<h1 style='text-align: center;'>📊 Comparador de Contratos</h1>",
    unsafe_allow_html=True
)

st.write("Faça upload das bases para identificar contratos que saíram.")

# ✅ UPLOAD DOS ARQUIVOS
base_antiga_file = st.file_uploader("Base Antiga", type=["csv", "xlsx"])
base_atual_file = st.file_uploader("Base Atual", type=["csv", "xlsx"])


# ✅ FUNÇÃO OTIMIZADA COM CACHE
@st.cache_data
def carregar_arquivo(arquivo):
    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(
            arquivo,
            sep=";",
            usecols=["CONTRATO", "RETENCAO"],
            dtype=str
        )
    else:
        df = pd.read_excel(
            arquivo,
            usecols=["CONTRATO", "RETENCAO"],
            dtype=str
        )

    # limpar colunas
    df.columns = df.columns.str.strip().str.upper()

    # limpar valores
    df["RETENCAO"] = df["RETENCAO"].str.strip().str.upper()

    # filtrar direto
    df = df[df["RETENCAO"] == "SIM"]

    # remover duplicados
    df = df.drop_duplicates(subset="CONTRATO")

    return df


# ✅ PROCESSAMENTO
if base_antiga_file and base_atual_file:

    base_antiga = carregar_arquivo(base_antiga_file)
