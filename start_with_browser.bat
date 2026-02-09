@echo off
REM Script para iniciar la app y abrir navegador automáticamente
cd /d "%~dp0"
start http://127.0.0.1:5000
timeout /t 2 /nobreak
.venv\Scripts\python.exe app.py
