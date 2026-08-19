import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Comparador de Contratos",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
div[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #dfe3e8;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

#LOGO
try:
    col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])

    with col_logo2:
        st.image("logo.JPG", width=250)
except:
    pass
st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0;'>
        Comparador de Contratos
    </h1>

    <p style='text-align:center;
                color:#666666;
                font-size:18px;'>
        Compare bases e identifique contratos removidos.
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

st.markdown("### 📅 Parâmetros de Projeção")

col1, col2 = st.columns(2)

with col1:
    dias_trabalhados = st.number_input(
        "Dias úteis até o período analisado",
        min_value=1.0,
        value=25.0
    )

with col2:
    dias_totais = st.number_input(
        "Total de dias úteis do mês",
        min_value=1.0,
        value=25.0
    )

st.markdown("### 📂 Upload das Bases")

col1, col2 = st.columns(2)

with col1:
    base_antiga = st.file_uploader(
        "📂 Base Antiga",
        type=["xlsx", "csv"]
    )

with col2:
    base_atual = st.file_uploader(
        "📂 Base Atual",
        type=["xlsx", "csv"]
    )

def ler_base(arquivo):
    if arquivo.name.lower().endswith(".csv"):
        df = pd.read_csv(
            arquivo,
            sep=";",
            dtype=str
        )
    else:
        df = pd.read_excel(
            arquivo,
            dtype=str
        )

    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    return df

st.markdown("---")
if st.button(
    "🚀 PROCESSAR CONTRATOS",
    use_container_width=True,
    type="primary"
):

    try:

        if not base_antiga or not base_atual:
            st.warning("Selecione as duas bases.")
            st.stop()

        antiga = ler_base(base_antiga)
        atual = ler_base(base_atual)

#Padroniza contrato
        antiga["CONTRATO"] = antiga["CONTRATO"].astype(str).str.strip()
        
        atual["CONTRATO"] = atual["CONTRATO"].astype(str).str.strip()

#Filtra apenas retençao = SIM
        antiga_filtrada = antiga[
            antiga["RETENCAO"]
            .str.strip()
            .str.upper()
            .eq("SIM")
        ].copy()

        atual_filtrada = atual[
            atual["RETENCAO"]
            .str.strip()
            .str.upper()
            .eq("SIM")
        ].copy()

#Remove duplicadas
        antiga_filtrada = antiga_filtrada.drop_duplicates(
            subset=["CONTRATO"],
            keep="first"
        )

        atual_filtrada = atual_filtrada.drop_duplicates(
            subset=["CONTRATO"],
            keep="first"
        )

# Mantém apenas a coluna contrato para comparação
        antiga_comp = antiga_filtrada[["CONTRATO"]]
        atual_comp = atual_filtrada[["CONTRATO"]]

        resultado = antiga_comp.merge(
            atual_comp,
            on="CONTRATO",
            how="left",
            indicator=True
        )

        resultado = resultado[
            resultado["_merge"] == "left_only"
        ]

        contratos_removidos = resultado["CONTRATO"]
        
        resultado_final = antiga_filtrada[
            antiga_filtrada["CONTRATO"]
            .isin(contratos_removidos)
        ].copy()

        base_calc = atual_filtrada.copy()

        base_calc["VIDAS"] = pd.to_numeric(
            base_calc["VIDAS"],
            errors="coerce"
        ).fillna(0)

        resumo = (
            base_calc
            .groupby("PORTE")["VIDAS"]
            .sum()
            .reset_index()
        )

        total_vidas = int(
            resumo["VIDAS"].sum()
        )
        projecao = int(
            (total_vidas / dias_trabalhados)
            * dias_totais
        )

        pf = int(
            resumo.loc[
                resumo["PORTE"] == "PF",
                "VIDAS"
            ].sum()
        )

        pme = int(
            resumo.loc[
                resumo["PORTE"] == "PME",
                "VIDAS"
            ].sum()
        )

        faltante = max(
            8000 - total_vidas,
            0
        )

        st.success(
            f"{len(resultado_final)} contratos removidos encontrados."
        )

        st.markdown("---")
        st.markdown("### 📊 Indicadores")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Removidos",
                f"{len(resultado_final):,}"
            )

        with col2:
            st.metric(
                "Total Vidas",
                f"{total_vidas:,}"
            )

        with col3:
            st.metric(
                "Projeção",
                f"{projecao:,}"
            )

        st.markdown("### 📌 Resumo")

        r1, r2, r3 = st.columns(3)

        with r1:
            st.metric(
                "Faltante para 8.000",
                f"{faltante:,}"
            )

        with r2:
            st.metric(
                "PF",
                f"{pf:,}"
            )

        with r3:
            st.metric(
                "PME",
                f"{pme:,}"
            )

        buffer = BytesIO()

        resultado_final.to_excel(
            buffer,
            index=False,
            engine="openpyxl"
        )

        st.download_button(
            label="📥 EXPORTAR EXCEL",
            data=buffer.getvalue(),
            file_name="contratos_removidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    except Exception as erro:
        st.error(str(erro))
