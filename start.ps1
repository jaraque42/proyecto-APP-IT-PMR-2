#!/usr/bin/env pwsh
# Script de inicio para la aplicación de entrega/recepción de teléfonos
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
.\.venv\Scripts\Activate.ps1
python app.py
