import streamlit as st
import pandas as pd
from io import BytesIO

# ✅ CONFIGURAÇÃO DA PÁGINA (fica mais profissional)
st.set_page_config(
    page_title="Comparador de Contratos",
    page_icon="📊",
    layout="centered"
)

# ✅ LOGO CENTRALIZADA
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.JPG", width=200)

# ✅ TÍTULO CENTRALIZADO
st.markdown(
    "<h1 style='text-align: center;'>📊 Comparador de Contratos</h1>",
    unsafe_allow_html=True
)

st.write("Faça upload das bases para identificar contratos que saíram.")

# Upload arquivos
base_antiga_file = st.file_uploader("Base Antiga", type=["csv", "xlsx"])
base_atual_file = st.file_uploader("Base Atual", type=["csv", "xlsx"])


# ✅ CACHE + LEITURA OTIMIZADA
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

    # filtrar direto (melhora MUITO performance)
    df = df[df["RETENCAO"] == "SIM"]

    # remover duplicados
    df = df.drop_duplicates(subset="CONTRATO")

    return df


if base_antiga_file and base_atual_file:

    base_antiga = carregar_arquivo(base_antiga_file)
    base_atual = carregar_arquivo(base_atual_file)

    # ✅ INFO DE TAMANHO
    st.write(f"Base antiga: {base_antiga.shape[0]} registros")
    st.write(f"Base atual: {base_atual.shape[0]} registros")

    if st.button("🚀 Processar"):

        with st.spinner("Processando dados..."):

            # comparação otimizada
            contratos_antigos = set(base_antiga["CONTRATO"].unique())
            contratos_atuais = set(base_atual["CONTRATO"].unique())

            contratos_removidos = contratos_antigos - contratos_atuais

            resultado = base_antiga[
                base_antiga["CONTRATO"].isin(contratos_removidos)
            ]

        st.success(f"✅ {len(resultado)} contratos removidos encontrados")

        # ✅ MOSTRAR PARTE DOS DADOS (evita travar)
        st.dataframe(resultado.head(100))
        st.info(f"Mostrando 100 de {len(resultado)} registros")

        # ✅ DOWNLOAD
        buffer = BytesIO()
        resultado.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar Excel completo",
            data=buffer,
            file_name="contratos_removidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )