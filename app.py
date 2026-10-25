"""
RENTRI Analyzer

Copyright (C) 2026 Gianluca Massei

Autore:
Gianluca Massei

Questo software è distribuito con licenza MIT.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from export_excel import genera_report_excel
from riepilogo_eer import genera_riepilogo_eer

from fifo import calcola_fifo
from analisi_tempi import verifica_tempi
from grafico_eta import grafico_eta


st.set_page_config(
    page_title="Analizzatore RENTRI",
    layout="wide"
)


# =====================================================
# FUNZIONI
# =====================================================

@st.cache_data
def carica_file(file):

    df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    df["Data registrazione"] = pd.to_datetime(
        df["Data registrazione"],
        dayfirst=True,
        errors="coerce"
    )

    df["Codice EER"] = (
        df["Codice EER"]
        .astype(str)
        .str.strip()
    )

    df["Tipo operazione"] = (
        df["Tipo operazione"]
        .astype(str)
        .str.strip()
    )

    df["Destinato a"] = (
        df["Destinato a"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["Quantita"] = pd.to_numeric(
        df["Quantita"],
        errors="coerce"
    )

    return df


def costruisci_movimenti(df):

    df = df.copy()

    df["Delta"] = df.apply(
        lambda r:
        r["Quantita"]
        if r["Tipo operazione"] == "Carico"
        else -r["Quantita"],
        axis=1
    )

    return df


# =====================================================
# INTERFACCIA
# =====================================================

st.title("Analizzatore RENTRI")

uploaded_file = st.file_uploader(
    "Carica esportazione RENTRI",
    type=["xlsx"]
)

if uploaded_file:

    df = carica_file(uploaded_file)

    st.success(
        f"Movimenti caricati: {len(df):,}"
    )

    eers = sorted(
        df["Codice EER"]
        .dropna()
        .unique()
    )

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.header("Parametri")

    eer = st.sidebar.selectbox(
        "Codice EER",
        eers
    )

    data_min = (
        df["Data registrazione"]
        .min()
        .date()
    )

    data_max = (
        df["Data registrazione"]
        .max()
        .date()
    )

    data_riferimento = st.sidebar.date_input(
        "Data riferimento giacenza",
        value=data_min,
        min_value=data_min,
        max_value=data_max
    )

    giacenza_iniziale = st.sidebar.number_input(
        "Giacenza iniziale (kg)",
        value=0.0
    )

    limite_istantaneo = st.sidebar.number_input(
        "Limite istantaneo (kg)",
        value=0.0
    )

    limite_annuo = st.sidebar.number_input(
        "Limite annuo (kg)",
        value=0.0
    )

    limite_giorni = st.sidebar.number_input(
        "Limite deposito (giorni)",
        value=365
    )

    OPERAZIONI_DEFAULT = [
        "R1","R2","R3","R4","R5",
        "R6","R7","R8","R9","R10",
        "D1","D2","D3","D4","D5",
        "D6","D7","D8","D9","D10",
        "D11","D12"
    ]

    operazioni_finali = st.sidebar.multiselect(
        "Operazioni considerate uscita definitiva",
        [
            "R1","R2","R3","R4","R5",
            "R6","R7","R8","R9","R10",
            "R11","R12","R13",
            "D1","D2","D3","D4","D5",
            "D6","D7","D8","D9","D10",
            "D11","D12","D13","D14","D15"
        ],
        default=OPERAZIONI_DEFAULT
    )

    # =====================================================
    # FILTRO EER
    # =====================================================

    eer_df = df[
        df["Codice EER"] == eer
    ].copy()

    eer_df = eer_df.sort_values(
        by=[
            "Data registrazione",
            "Progressivo"
        ]
    )

    eer_df = costruisci_movimenti(
        eer_df
    )

    # =====================================================
    # GIACENZA
    # =====================================================

    data_riferimento = pd.Timestamp(
        data_riferimento
    )

    prima = eer_df[
        eer_df["Data registrazione"]
        < data_riferimento
    ]

    saldo_precedente = (
        prima["Delta"]
        .sum()
    )

    offset = (
        giacenza_iniziale
        - saldo_precedente
    )

    eer_df["Giacenza"] = (
        offset +
        eer_df["Delta"]
        .cumsum()
    )

    # =====================================================
    # KPI
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    giacenza_max = (
        eer_df["Giacenza"].max()
    )

    totale_carichi = (
        eer_df[
            eer_df["Tipo operazione"]
            == "Carico"
        ]["Quantita"]
        .sum()
    )

    totale_scarichi = (
        eer_df[
            eer_df["Tipo operazione"]
            == "Scarico"
        ]["Quantita"]
        .sum()
    )

    col1.metric(
        "Giacenza max",
        f"{giacenza_max:,.0f}"
    )

    col2.metric(
        "Carichi",
        f"{totale_carichi:,.0f}"
    )

    col3.metric(
        "Scarichi",
        f"{totale_scarichi:,.0f}"
    )

    col4.metric(
        "Movimenti",
        len(eer_df)
    )

    # =====================================================
    # GRAFICO GIACENZA
    # =====================================================

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=eer_df["Data registrazione"],
            y=eer_df["Giacenza"],
            mode="lines+markers",
            name="Giacenza"
        )
    )

    if limite_istantaneo > 0:

        fig.add_hline(
            y=limite_istantaneo,
            line_color="red"
        )

    fig.update_layout(
        title=f"Giacenza EER {eer}",
        height=600
    )

    # =====================================================
    # ANALISI FIFO
    # =====================================================

    fifo_input = eer_df[
        (
            eer_df["Tipo operazione"]
            == "Carico"
        )
        |
        (
            (
                eer_df["Tipo operazione"]
                == "Scarico"
            )
            &
            (
                eer_df["Destinato a"]
                .isin(operazioni_finali)
            )
        )
    ].copy()

    fifo_df = pd.DataFrame()
    residui_df = pd.DataFrame()

    if len(fifo_input):

        fifo_df, residui_df = calcola_fifo(
            fifo_input
        )

        if not fifo_df.empty:

            fifo_df = verifica_tempi(
                fifo_df,
                limite_giorni
            )

    # =====================================================
    # CARICHI ANNUI
    # =====================================================

    carichi_annui = (
        eer_df[
            eer_df["Tipo operazione"]
            == "Carico"
        ]
        .groupby(
            eer_df["Data registrazione"]
            .dt.year
        )["Quantita"]
        .sum()
        .reset_index()
    )

    carichi_annui.columns = [
        "Anno",
        "Carichi"
    ]

    fig_annuo = px.bar(
        carichi_annui,
        x="Anno",
        y="Carichi"
    )

    if limite_annuo > 0:

        fig_annuo.add_hline(
            y=limite_annuo,
            line_color="red"
        )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Grafici",
            "Anomalie",
            "FIFO",
            "Movimenti",
            "Report",
            "Riepilogo Impianto"
        ]
    )

    with tab1:

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.plotly_chart(
            fig_annuo,
            use_container_width=True
        )

        if not fifo_df.empty:

            fig_eta = grafico_eta(
                fifo_df,
                limite_giorni
            )

            st.plotly_chart(
                fig_eta,
                use_container_width=True
            )

    with tab2:

        if not fifo_df.empty:

            anomalie_fifo = fifo_df[
                fifo_df["Superamento"]
            ]

            st.dataframe(
                anomalie_fifo,
                use_container_width=True
            )

        else:

            st.info(
                "Nessuna anomalia rilevata"
            )

    with tab3:

        st.subheader(
            "Movimenti FIFO"
        )

        st.dataframe(
            fifo_df,
            use_container_width=True
        )

        st.subheader(
            "Lotti residui"
        )

        st.dataframe(
            residui_df,
            use_container_width=True
        )

    with tab4:

        st.dataframe(
            eer_df,
            use_container_width=True
        )

    with tab5:

        st.subheader("Generazione report Excel")

        if st.button("Genera report Excel"):

            try:

                report_file = genera_report_excel(
                    eer=eer,
                    movimenti_df=eer_df,
                    fifo_df=fifo_df,
                    residui_df=residui_df,
                    operazioni_finali=operazioni_finali,
                    limite_istantaneo=limite_istantaneo,
                    limite_giorni=limite_giorni,
                    output_file="report.xlsx"
                )

                st.success(
                    "Report generato correttamente"
                )

                with open(
                    report_file,
                    "rb"
                ) as f:

                    st.download_button(
                        label="Scarica report.xlsx",
                        data=f,
                        file_name=f"report_{eer}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:

                st.error(
                    f"Errore export: {e}"
                )

    with tab6:

        st.subheader(
            "Riepilogo multi-EER"
        )

        st.write(
            """
            Genera un file Excel contenente,
            per ogni codice EER:
            
            - giacenza massima
            - data della giacenza massima
            - quantitativo annuo movimentato
            - permanenza massima
            - numero movimenti
            - numero lotti residui
            """
        )

        if st.button(
            "Genera riepilogo impianto"
        ):

            try:

                file_riepilogo = genera_riepilogo_eer(
                    df=df,
                    operazioni_finali=operazioni_finali,
                    output_file="riepilogo_eer.xlsx"
                )

                st.success(
                    "Riepilogo generato correttamente"
                )

                with open(
                    file_riepilogo,
                    "rb"
                ) as f:

                    st.download_button(
                        label="Scarica riepilogo_eer.xlsx",
                        data=f,
                        file_name="riepilogo_eer.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:

                st.error(
                    f"Errore: {e}"
                )