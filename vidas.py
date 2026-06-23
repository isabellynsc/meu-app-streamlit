import streamlit as st
import pandas as pd

st.title("📊 Comparador de Contratos")

st.write("Faça upload das bases para identificar contratos que saíram.")

# Upload arquivos
base_antiga_file = st.file_uploader("Base Antiga", type=["csv", "xlsx"])
base_atual_file = st.file_uploader("Base Atual", type=["csv", "xlsx"])

def carregar_arquivo(arquivo):
    if arquivo.name.endswith(".csv"):
        return pd.read_csv(arquivo, sep=";")
    else:
        return pd.read_excel(arquivo)

if base_antiga_file and base_atual_file:

    base_antiga = carregar_arquivo(base_antiga_file)
    base_atual = carregar_arquivo(base_atual_file)

    # limpar colunas
    base_antiga.columns = base_antiga.columns.str.strip().str.upper()
    base_atual.columns = base_atual.columns.str.strip().str.upper()

    # botão
    if st.button("🚀 Processar"):

        # filtro
        base_antiga = base_antiga[base_antiga["RETENCAO"].str.upper().str.strip() == "SIM"]
        base_atual = base_atual[base_atual["RETENCAO"].str.upper().str.strip() == "SIM"]

        # remover duplicados
        base_antiga = base_antiga.drop_duplicates(subset="CONTRATO")
        base_atual = base_atual.drop_duplicates(subset="CONTRATO")

        # comparação
        contratos_removidos = set(base_antiga["CONTRATO"]) - set(base_atual["CONTRATO"])

        resultado = base_antiga[base_antiga["CONTRATO"].isin(contratos_removidos)]

        st.success(f"✅ {len(resultado)} contratos removidos encontrados")

        # mostrar tabela
        st.dataframe(resultado)

        # botão download
        
        from io import BytesIO

        buffer = BytesIO()
        resultado.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name="contratos_removidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )