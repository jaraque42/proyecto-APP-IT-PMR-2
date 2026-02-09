@echo off
REM Script de instalación del entorno virtual (ejecutar UNA SOLA VEZ)
cd /d "%~dp0"
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
echo.
echo Instalacion completada. Ahora puedes hacer doble clic en start.bat para iniciar la app.
pause
