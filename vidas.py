import streamlit as st
import pandas as pd

st.title("📊 Comparador de Contratos")
st.write("Faça upload das bases para identificar contratos que saíram.")

# Upload arquivos
base_antiga_file = st.file_uploader("Base Antiga", type=["csv", "xlsx"])
base_atual_file = st.file_uploader("Base Atual", type=["csv", "xlsx"])


# ✅ CACHE (isso faz MUITA diferença)
@st.cache_data
def carregar_arquivo(arquivo):
    if arquivo.name.endswith(".csv"):
        return pd.read_csv(
            arquivo,
            sep=";",
            usecols=["CONTRATO", "RETENCAO"],  # 🔥 carrega só o necessário
            dtype=str  # 🔥 evita problemas de memória
        )
    else:
        return pd.read_excel(
            arquivo,
            usecols=["CONTRATO", "RETENCAO"],
            dtype=str
        )


if base_antiga_file and base_atual_file:

    base_antiga = carregar_arquivo(base_antiga_file)
    base_atual = carregar_arquivo(base_atual_file)

    # limpar colunas
    base_antiga.columns = base_antiga.columns.str.strip().str.upper()
    base_atual.columns = base_atual.columns.str.strip().str.upper()

    if st.button("🚀 Processar"):

        # ✅ limpar dados de forma mais leve
        base_antiga["RETENCAO"] = base_antiga["RETENCAO"].str.strip().str.upper()
        base_atual["RETENCAO"] = base_atual["RETENCAO"].str.strip().str.upper()

        # filtro
        base_antiga = base_antiga[base_antiga["RETENCAO"] == "SIM"]
        base_atual = base_atual[base_atual["RETENCAO"] == "SIM"]

        # remover duplicados (mais eficiente)
        base_antiga = base_antiga.drop_duplicates(subset="CONTRATO")
        base_atual = base_atual.drop_duplicates(subset="CONTRATO")

        # ✅ converter para set direto (mais leve)
        contratos_antigos = set(base_antiga["CONTRATO"])
        contratos_atuais = set(base_atual["CONTRATO"])

        contratos_removidos = contratos_antigos - contratos_atuais

        resultado = base_antiga[base_antiga["CONTRATO"].isin(contratos_removidos)]

        st.success(f"✅ {len(resultado)} contratos removidos encontrados")

        st.dataframe(resultado)

        # download
        from io import BytesIO

        buffer = BytesIO()
        resultado.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name="contratos_removidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )