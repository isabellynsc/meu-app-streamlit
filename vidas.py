import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Comparador de Contratos",
    layout="wide"
)

st.title("Comparador de Contratos")
st.write("Faça upload das bases para identificar contratos removidos.")

dias_trabalhados = st.number_input(
    "Dias úteis até o período analisado",
    min_value=1.0,
    value=23.0
)

dias_totais = st.number_input(
    "Total de dias úteis do mês",
    min_value=1.0,
    value=23.0
)

base_antiga = st.file_uploader(
    "Base Antiga",
    type=["xlsx", "csv"]
)

base_atual = st.file_uploader(
    "Base Atual",
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


if st.button("🚀 PROCESSAR"):

    try:

        if not base_antiga or not base_atual:
            st.warning("Selecione as duas bases.")
            st.stop()

        antiga = ler_base(base_antiga)
        atual = ler_base(base_atual)

        antiga_filtrada = antiga[
            antiga["RETENCAO"]
            .str.strip()
            .str.upper()
            .eq("SIM")
        ][["CONTRATO"]].drop_duplicates()

        atual_filtrada = atual[
            atual["RETENCAO"]
            .str.strip()
            .str.upper()
            .eq("SIM")
        ][["CONTRATO"]].drop_duplicates()

        resultado = antiga_filtrada.merge(
            atual_filtrada,
            on="CONTRATO",
            how="left",
            indicator=True
        )

        resultado = resultado[
            resultado["_merge"] == "left_only"
        ]

        contratos_removidos = resultado["CONTRATO"]
        
        resultado_final = antiga[
            antiga["CONTRATO"]
            .isin(contratos_removidos)
        ].copy()

        base_calc = atual.copy()

        base_calc = base_calc[
            base_calc["RETENCAO"]
            .str.strip()
            .str.upper()
            .eq("SIM")
        ]

        base_calc = base_calc.drop_duplicates(
            subset="CONTRATO"
        )


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
            10000 - total_vidas,
            0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Removidos",
            len(resultado_final)
        )

        col2.metric(
            "Total Vidas",
            total_vidas
        )

        col3.metric(
            "Projeção",
            projecao
        )

        st.success(
            f"{len(resultado_final)} contratos removidos encontrados."
        )

        st.write(
            f"🎯 Faltante para 10.000: {faltante:,}"
        )

        st.write(
            f"👤 PF: {pf:,}"
        )

        st.write(
            f"🏢 PME: {pme:,}"
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as erro:
        st.error(str(erro))