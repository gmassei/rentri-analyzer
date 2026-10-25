"""
RENTRI Analyzer

Copyright (C) 2026 Gianluca Massei

Autore:
Gianluca Massei

Questo software è distribuito con licenza MIT.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"""
import pandas as pd


def verifica_tempi(
    fifo_df,
    limite_giorni
):

    fifo_df = fifo_df.copy()

    fifo_df["Superamento"] = (
        fifo_df["GiorniDeposito"]
        > limite_giorni
    )

    return fifo_df