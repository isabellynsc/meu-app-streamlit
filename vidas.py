import streamlit as st
import pandas as pd
from io import BytesIO

# ✅ CONFIGURAÇÃO
st.set_page_config(
    page_title="Comparador de Contratos",
    page_icon="📊",
    layout="centered"
)

# ✅ LOGO CENTRALIZADA E SEGURA
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.JPG", width=200)
    except:
        st.write("")

# ✅ TÍTULO
st.markdown(
    "<h1 style='text-align: center;'>📊 Comparador de Contratos</h1>",
    unsafe_allow_html=True
)

st.write("Faça upload das bases para identificar contratos que saíram.")

# ✅ UPLOAD
base_antiga_file = st.file_uploader("Base Antiga", type=["csv", "xlsx"])
base_atual_file = st.file_uploader("Base Atual", type=["csv", "xlsx"])


# ✅ FUNÇÃO OTIMIZADA
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

    df.columns = df.columns.str.strip().str.upper()

    # ✅ filtro mais rápido
    mask = df["RETENCAO"].str.strip().str.upper().eq("SIM")
    df = df.loc[mask, ["CONTRATO"]]

    return df.drop_duplicates()


# ✅ FLUXO CORRETO (BOTÃO APARECE SEM TRAVAR)
if base_antiga_file and base_atual_file:

    st.success("✅ Arquivos carregados! Agora clique no botão para processar.")

    if st.button("🚀 Processar"):

        with st.spinner("Processando dados..."):

            base_antiga = carregar_arquivo(base_antiga_file)
            base_atual = carregar_arquivo(base_atual_file)

            st.write(f"Base antiga: {len(base_antiga)} registros")
            st.write(f"Base atual: {len(base_atual)} registros")

            # ✅ comparação mais eficiente (pandas)
            resultado = base_antiga.merge(
                base_atual,
                on="CONTRATO",
                how="left",
                indicator=True
            )

            resultado = resultado[resultado["_merge"] == "left_only"]
            resultado = resultado.drop(columns=["_merge"])

        st.success(f"✅ {len(resultado)} contratos removidos encontrados")

        # ✅ MOSTRAR MENOS DADOS (performance)
        st.dataframe(resultado.head(50))
        st.info(f"Mostrando 50 de {len(resultado)} registros")

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