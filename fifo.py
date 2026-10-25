"""
RENTRI Analyzer

Copyright (C) 2026 Gianluca Massei

Autore:
Gianluca Massei

Questo software è distribuito con licenza MIT.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"""

from collections import deque
import pandas as pd


def calcola_fifo(
    df_movimenti: pd.DataFrame
):

    lotti = deque()

    movimenti_fifo = []

    giacenze_residue = []

    for _, row in df_movimenti.iterrows():

        data_mov = row["Data registrazione"]

        qta = float(row["Quantita"])

        operazione = row["Tipo operazione"]

        progressivo = row["Progressivo"]

        if operazione == "Carico":

            lotto = {

                "DataCarico": data_mov,

                "ProgressivoCarico": progressivo,

                "QuantitaIniziale": qta,

                "Residuo": qta

            }

            lotti.append(lotto)

        elif operazione == "Scarico":

            residuo_scarico = qta

            while residuo_scarico > 0 and len(lotti) > 0:

                lotto = lotti[0]

                prelevata = min(
                    residuo_scarico,
                    lotto["Residuo"]
                )

                giorni = (
                    data_mov -
                    lotto["DataCarico"]
                ).days

                movimenti_fifo.append({

                    "DataCarico":
                        lotto["DataCarico"],

                    "ProgressivoCarico":
                        lotto[
                            "ProgressivoCarico"
                        ],

                    "DataScarico":
                        data_mov,

                    "ProgressivoScarico":
                        progressivo,

                    "Quantita":
                        prelevata,

                    "GiorniDeposito":
                        giorni

                })

                lotto["Residuo"] -= prelevata

                residuo_scarico -= prelevata

                if lotto["Residuo"] <= 0:

                    lotti.popleft()

    for lotto in lotti:

        giacenze_residue.append({

            "DataCarico":
                lotto["DataCarico"],

            "ProgressivoCarico":
                lotto[
                    "ProgressivoCarico"
                ],

            "QuantitaResidua":
                lotto["Residuo"]

        })

    df_fifo = pd.DataFrame(
        movimenti_fifo
    )

    df_residui = pd.DataFrame(
        giacenze_residue
    )

    return df_fifo, df_residui