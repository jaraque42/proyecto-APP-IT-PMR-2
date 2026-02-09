import csv
import io
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'entregas.db')
CSV_PATH = os.path.join(BASE_DIR, 'sample_import.csv')

def _get_value(row, keys):
    if not row:
        return ''
    for k in keys:
        if k in row and row[k] is not None:
            return str(row[k]).strip()
    lower_map = { (str(kk).lower() if kk is not None else ''): vv for kk,vv in row.items() }
    for k in keys:
        kk = k.lower()
        if kk in lower_map and lower_map[kk] is not None:
            return str(lower_map[kk]).strip()
    return ''

def main():
    if not os.path.exists(CSV_PATH):
        print('No existe', CSV_PATH)
        return
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print('No hay filas en el CSV')
        return

    conn = sqlite3.connect(DB_PATH)
    inserted = 0
    for r in rows:
        imei = _get_value(r, ['imei', 'IMEI'])
        telefono = _get_value(r, ['telefono', 'phone', 'telefono_movil'])
        numero_serie = _get_value(r, ['numero_serie', 'serie', 'serial'])
        modelo = _get_value(r, ['modelo', 'model'])
        usuario = _get_value(r, ['usuario', 'user', 'nombre'])
        tipo = _get_value(r, ['tipo', 'type']) or 'entrega'
        timestamp = datetime.utcnow().isoformat()
        conn.execute('INSERT INTO entregas (imei, telefono, numero_serie, modelo, usuario, tipo, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (imei, telefono, numero_serie, modelo, usuario, tipo, timestamp))
        inserted += 1
    conn.commit()
    conn.close()
    print(f'Insertados: {inserted}')

if __name__ == '__main__':
    main()
