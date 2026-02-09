import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'entregas.db')

def main():
    if not os.path.exists(DB_PATH):
        print('No existe la base de datos en', DB_PATH)
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT id, tipo, imei, telefono, numero_serie, modelo, usuario, timestamp FROM entregas ORDER BY timestamp DESC')
    rows = cur.fetchall()
    print(f'Total registros: {len(rows)}')
    for r in rows[:50]:
        print(r)
    conn.close()

if __name__ == "__main__":
    main()
