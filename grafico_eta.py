"""
RENTRI Analyzer

Copyright (C) 2026 Gianluca Massei

Autore:
Gianluca Massei

Questo software è distribuito con licenza MIT.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"""
import plotly.graph_objects as go


def grafico_eta(
    fifo_df,
    limite_giorni
):

    eta = (
        fifo_df
        .groupby("DataScarico")
        ["GiorniDeposito"]
        .max()
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=eta["DataScarico"],
            y=eta["GiorniDeposito"],
            mode="lines+markers",
            name="Età massima lotto"
        )
    )

    fig.add_hline(
        y=limite_giorni,
        line_color="red"
    )

    fig.update_layout(
        title="Età massima dei lotti",
        xaxis_title="Data",
        yaxis_title="Giorni"
    )

    return fig