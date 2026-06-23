import streamlit as st
import pandas as pd
from io import BytesIO

# ✅ CONFIGURAÇÃO
st.set_page_config(
    page_title="Comparador de Contratos",
    page_icon="flor_icon.png",
    layout="centered"
)

# ✅ HEADER (TOPO FUNCIONAL)
topo_col1, topo_col2 = st.columns([1, 8])

with topo_col1:
    try:
        st.image("logo.png", width=90)
    except:
        st.write("")

with topo_col2:
    st.markdown(
        "<h1 style='margin-top:0px;'>Comparador de Contratos</h1>",
        unsafe_allow_html=True
    )

st.write("Faça upload das bases para identificar contratos que saíram.")

# ✅ PARÂMETROS
st.subheader("📅 Parâmetros de Projeção")

colA, colB = st.columns(2)

dias_trabalhados = colA.number_input(
    "Dias úteis até o período analisado",
    min_value=0.0,
    step=0.5
)

dias_totais = colB.number_input(
    "Total de dias úteis do mês",
    min_value=0.0,
    step=0.5
)

st.caption("Sábado conta como 0.5 dia. Domingos e feriados não entram.")

# ✅ UPLOAD
base_antiga_file = st.file_uploader("Base Antiga", type=["csv", "xlsx"])
base_atual_file = st.file_uploader("Base Atual", type=["csv", "xlsx"])


# ✅ FUNÇÃO CONTRATOS
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

    mask = df["RETENCAO"].str.strip().str.upper().eq("SIM")
    df = df.loc[mask, ["CONTRATO"]]

    return df.drop_duplicates()


# ✅ FUNÇÃO BASE COMPLETA
@st.cache_data
def carregar_base_completa(arquivo):
    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(arquivo, sep=";", dtype=str)
    else:
        df = pd.read_excel(arquivo, dtype=str)

    df.columns = df.columns.str.strip().str.upper()

    df = df[df["RETENCAO"].str.strip().str.upper() == "SIM"]
    df = df.drop_duplicates(subset="CONTRATO")

    df["VIDAS"] = pd.to_numeric(df["VIDAS"], errors="coerce").fillna(0)

    return df


# ✅ EXECUÇÃO
if base_antiga_file and base_atual_file:

    st.success("✅ Arquivos carregados! Clique para processar.")

    if st.button("🚀 Processar"):

        if dias_trabalhados == 0 or dias_totais == 0:
            st.warning("⚠️ Informe os dias úteis para calcular a projeção.")
        else:

            with st.spinner("Processando dados..."):

                # 🔹 CONTRATOS REMOVIDOS
                base_antiga = carregar_arquivo(base_antiga_file)
                base_atual = carregar_arquivo(base_atual_file)

                resultado = base_antiga.merge(
                    base_atual,
                    on="CONTRATO",
                    how="left",
                    indicator=True
                )

                resultado = resultado[resultado["_merge"] == "left_only"]
                resultado = resultado.drop(columns=["_merge"])

                # 🔹 BASE DE VIDAS
                base_calc = carregar_base_completa(base_atual_file)

                resumo = base_calc.groupby("PORTE")["VIDAS"].sum().reset_index()

                total_vidas = int(resumo["VIDAS"].sum())

                projecao = int((total_vidas / dias_trabalhados) * dias_totais)

                meta = 10000
                faltante = max(meta - total_vidas, 0)

            # ✅ RESULTADOS
            st.success(f"✅ {len(resultado)} contratos removidos encontrados")

            st.dataframe(resultado.head(50))
            st.info(f"Mostrando 50 de {len(resultado)} registros")

            buffer = BytesIO()
            resultado.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            st.download_button(
                label="📥 Baixar Excel completo",
                data=buffer,
                file_name="contratos_removidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # ✅ DASHBOARD
            st.subheader("📊 Resumo de Vidas")

            col1, col2, col3 = st.columns(3)

            col1.metric("Total de Vidas", total_vidas)
            col2.metric("Projeção do Mês", projecao)
            col3.metric("Faltante p/ 10.000", faltante)

            st.dataframe(resumo)

            st.write(f"**Total Geral: {total_vidas}**")

            if faltante > 0:
                st.warning(f"Faltam {faltante} vidas para atingir a meta de 10.000")
            else:
                st.success("✅ Meta atingida!")