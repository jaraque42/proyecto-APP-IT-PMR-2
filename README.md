# Entrega y Recepción de Teléfonos (Minimal)

Pequeña aplicación web para registrar entrega y recepción de teléfonos móviles.

## Inicio Rápido (Uso Diario)

Haz **doble clic** en `start.bat` para iniciar la aplicación automáticamente.
- Se abrirá una ventana de terminal mostrando el servidor en `http://127.0.0.1:5000`.
- Abre tu navegador en esa URL.
- Cierra la ventana de terminal cuando termines.

## Requisitos Iniciales (Una Sola Vez)
- Python 3.8+ instalado
- Ejecutar `install.bat` la primera vez para crear el entorno virtual

## Ejecución Manual (PowerShell en Windows)
```powershell
cd C:\Users\madpmr07\Desktop\APP-IT-PMR
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Luego abre `http://127.0.0.1:5000` en tu navegador.

## Características
- **Entrega**: Registra teléfonos que salen del almacén
- **Recepción**: Registra teléfonos que entran al almacén
- **Histórico**: Tabla con todos los registros (IMEI, teléfono, número de serie, modelo, usuario, tipo, fecha)
- **Importar**: Carga múltiples registros desde un archivo CSV o XLSX
- **Base de datos local**: `entregas.db` (SQLite, creada automáticamente)

## Formatos de Importación
Archivos CSV o XLSX deben incluir encabezados (case-insensitive):
- `imei` (requerido)
- `telefono`
- `numero_serie`
- `modelo`
- `usuario` (requerido)
- `tipo` (opcional: `entrega` o `recepcion`, por defecto `entrega`)
