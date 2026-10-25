# rentri-analyzer
# RENTRI Analyzer

Analizzatore avanzato di esportazioni RENTRI per la verifica di giacenze, quantitativi movimentati e tempi di permanenza dei rifiuti.

**Autore:** Gianluca Massei  
**Licenza:** MIT License  
**Versione:** 1.0

---

# Finalità

RENTRI Analyzer è uno strumento sviluppato per l'analisi tecnica delle esportazioni del Registro Elettronico Nazionale per la Tracciabilità dei Rifiuti (RENTRI).

L'applicazione consente di:

- ricostruire le giacenze istantanee;
- verificare i quantitativi annui movimentati;
- calcolare la permanenza dei rifiuti mediante algoritmo FIFO;
- individuare superamenti quantitativi e temporali;
- produrre report Excel;
- generare riepiloghi multi-EER.

L'applicazione è stata concepita come supporto alle attività di controllo, verifica autorizzativa e ispezione ambientale.

---

# Architettura del progetto

| File | Descrizione |
|--------|--------|
| `app.py` | Interfaccia Streamlit e logica principale |
| `fifo.py` | Algoritmo FIFO |
| `analisi_tempi.py` | Verifica tempi di permanenza |
| `grafico_eta.py` | Grafico età massima lotti |
| `export_excel.py` | Esportazione report Excel |
| `riepilogo_eer.py` | Generazione riepilogo multi-EER |

---

# Requisiti

```bash
pip install streamlit pandas plotly openpyxl
```

oppure

```bash
pip install -r requirements.txt
```

---

# Avvio

```bash
python -m streamlit run app.py
```

oppure mediante il file:

```text
run_rentri.bat
```

---

# Formato dei dati di input

L'applicazione utilizza esportazioni RENTRI in formato:

```text
.xlsx
```

Le seguenti colonne devono essere presenti:

| Campo |
|---------|
| Data registrazione |
| Progressivo |
| Tipo operazione |
| Codice EER |
| Quantita |
| Destinato a |

---

# Parametri di analisi

## Codice EER

Identifica il codice rifiuto oggetto dell'analisi.

Tutte le elaborazioni vengono effettuate sul codice selezionato.

---

## Data riferimento giacenza

Data alla quale viene associata la giacenza iniziale.

Consente di riallineare l'elaborazione a:

- MUD;
- verifiche ispettive;
- inventari;
- comunicazioni del gestore.

---

## Giacenza iniziale

Quantitativo presente alla data di riferimento.

Unità di misura:

```text
kg
```

---

## Limite istantaneo

Quantitativo massimo autorizzato contemporaneamente presente in deposito.

Viene utilizzato per:

- grafico giacenze;
- identificazione anomalie;
- report Excel.

---

## Limite annuo

Quantitativo massimo autorizzato annualmente movimentabile.

---

## Limite deposito

Numero massimo di giorni di permanenza consentiti.

---

## Operazioni considerate uscita definitiva

L'algoritmo FIFO associa gli scarichi ai lotti soltanto se il campo:

```text
Destinato a
```

contiene una delle operazioni selezionate.

Esempi:

```text
R1
R2
R3
R4
R5
D8
D9
D10
```

---

# Algoritmo FIFO

L'applicazione utilizza il criterio:

```text
First In - First Out
```

Ogni registrazione di carico genera un lotto virtuale.

Gli scarichi appartenenti alle operazioni finali selezionate consumano progressivamente i lotti più vecchi.

## Esempio

Carichi:

```text
01/01  10.000 kg
10/01   5.000 kg
```

Scarico:

```text
15/03  12.000 kg
```

Associazione FIFO:

```text
10.000 kg → lotto del 01/01
 2.000 kg → lotto del 10/01
```

---

# Indicatori calcolati

Per ogni codice EER vengono determinati:

## Giacenza massima

Massima quantità contemporaneamente presente in deposito.

---

## Data della giacenza massima

Data nella quale viene raggiunto il massimo accumulo.

---

## Quantitativo annuo

Somma dei carichi registrati nel periodo analizzato.

---

## Giorni massimi di deposito

Massima permanenza rilevata dall'algoritmo FIFO.

---

## Numero movimenti

