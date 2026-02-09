import sqlite3
import os
import sys
# Asegurar que el directorio raíz del proyecto está en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, DB_PATH

TEST_IMEI = 'TEST-IMEI-0001'

# Limpiar registros previos para asegurar idempotencia
with app.app_context():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM entregas WHERE imei = ?', (TEST_IMEI,))
    conn.commit()
    conn.close()

# Desactivar login_required para pruebas automatizadas
app.config['LOGIN_DISABLED'] = True
with app.test_client() as c:
    # Simular usuario con permisos parcheando la función interna de flask_login (sólo para pruebas)
    import flask_login
    from app import User
    flask_login.utils._get_user = lambda: User(1, 'admin', 'admin')

    # Primera entrega (debe generar PDF)
    print('LOGIN_DISABLED:', app.config.get('LOGIN_DISABLED'))
    data = {'situm':'S1', 'usuario':'Tester', 'imei':TEST_IMEI, 'telefono':'600000000', 'notas_telefono':'Nota'}
    r1 = c.post('/entrega', data=data)
    print('First entrega status:', r1.status_code, 'content-type:', r1.content_type)
    if r1.content_type == 'application/pdf':
        out_path = os.path.join(os.getcwd(), 'test_entrega_first.pdf')
        with open(out_path, 'wb') as f:
            f.write(r1.data)
        print('PDF generated:', out_path)
    else:
        print('Unexpected first entrega response:', r1.data[:200])

    # Comprobar filas en BD **después de la primera inserción**
    with app.app_context():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT id, tipo, timestamp FROM entregas WHERE imei = ? ORDER BY timestamp DESC', (TEST_IMEI,))
        rows_after_first = cur.fetchall()
        print('DB rows after first entrega:')
        for row in rows_after_first:
            print(dict(row))
        conn.close()

    # Segunda entrega (debe ser bloqueada y redirigir con flash)
    r2 = c.post('/entrega', data=data, follow_redirects=True)
    print('Second entrega status:', r2.status_code)

    # Buscar el mensaje dentro de window.server_messages (script JSON)
    import re, json
    m = re.search(rb'window\.server_messages\s*=\s*(\[.*?\]);', r2.data, flags=re.S)
    expected_text = f'No se puede registrar la entrega: el dispositivo con IMEI {TEST_IMEI} no ha sido recepcionado aún.'
    if m:
        msgs = json.loads(m.group(1).decode('utf-8'))
        print('server_messages:', msgs)
        found = any(expected_text == pair[1] for pair in msgs)
        if found:
            print('Flash message found inside server_messages JSON.')
        else:
            print('Flash not found in server_messages JSON.')
    else:
        print('No window.server_messages found in response. Response snippet:')
        print(r2.data.decode('utf-8')[:800])

    # Información final: listar últimos registros para este IMEI
    with app.app_context():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT id, tipo, timestamp FROM entregas WHERE imei = ? ORDER BY timestamp DESC', (TEST_IMEI,))
        rows = cur.fetchall()
        print('\nDB rows for IMEI:', TEST_IMEI)
        for row in rows:
            print(dict(row))
        conn.close()
