import sqlite3
conn = sqlite3.connect('entregas.db')
cur = conn.cursor()
cur.execute('SELECT id, username, rol, activo, fecha_creacion, password FROM usuarios')
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
