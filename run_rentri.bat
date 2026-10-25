@echo off

title Analizzatore RENTRI

cd /d "%~dp0"

call C:\ProgramData\miniconda3\Scripts\activate.bat

call conda activate rentri

python -m streamlit run app.py

pause