import sqlite3
import sys
if len(sys.argv) < 2:
    print('')
    sys.exit(0)
username = sys.argv[1]
conn = sqlite3.connect('entregas.db')
cur = conn.cursor()
cur.execute('SELECT id FROM usuarios WHERE username=?',(username,))
row = cur.fetchone()
if row:
    print(row[0])
else:
    print('')
conn.close()
