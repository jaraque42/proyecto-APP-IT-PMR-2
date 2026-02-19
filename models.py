"""Modelos, conexión a BD e inicialización de esquema."""

import os
import sqlite3
from datetime import datetime

from flask import g
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'entregas.db')

# ---------------------------------------------------------------------------
# Conexión a BD
# ---------------------------------------------------------------------------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')  # Mejor rendimiento concurrente
    return db


def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------------------------------------------------------------------------
# Modelo de usuario
# ---------------------------------------------------------------------------

ROLES_PERMISOS = {
    'admin': [
        'crear_usuario', 'eliminar_usuario', 'cambiar_rol',
        'registrar', 'borrar_registros', 'ver_historico',
        'ver_incidencias', 'administracion',
    ],
    'operator': ['registrar', 'borrar_registros', 'ver_historico', 'ver_incidencias'],
    'viewer': ['ver_historico', 'ver_incidencias'],
}


class User(UserMixin):
    def __init__(self, id, username, rol):
        self.id = id
        self.username = username
        self.rol = rol

    def tiene_permiso(self, permiso):
        return permiso in ROLES_PERMISOS.get(self.rol, [])

# ---------------------------------------------------------------------------
# Inicialización de esquema
# ---------------------------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- entregas ---
    cursor.execute("PRAGMA table_info(entregas)")
    columns = [c[1] for c in cursor.fetchall()]

    if columns and 'numero_serie' in columns:
        conn.execute('''
            CREATE TABLE entregas_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                situm TEXT, usuario TEXT, imei TEXT,
                telefono TEXT, notas_telefono TEXT,
                tipo TEXT, timestamp TEXT
            )
        ''')
        conn.execute('''
            INSERT INTO entregas_new (situm, usuario, imei, telefono, notas_telefono, tipo, timestamp)
            SELECT '', usuario, imei, telefono, modelo, tipo, timestamp FROM entregas
        ''')
        conn.execute('DROP TABLE entregas')
        conn.execute('ALTER TABLE entregas_new RENAME TO entregas')
    elif not columns:
        conn.execute('''
            CREATE TABLE entregas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                situm TEXT, usuario TEXT, imei TEXT,
                telefono TEXT, notas_telefono TEXT,
                tipo TEXT, timestamp TEXT,
                codigo_validacion TEXT, email_usuario TEXT
            )
        ''')
    else:
        if 'codigo_validacion' not in columns:
            conn.execute("ALTER TABLE entregas ADD COLUMN codigo_validacion TEXT")
        if 'email_usuario' not in columns:
            conn.execute("ALTER TABLE entregas ADD COLUMN email_usuario TEXT")

    # --- validaciones_email ---
    cursor.execute("PRAGMA table_info(validaciones_email)")
    if not cursor.fetchall():
        conn.execute('''
            CREATE TABLE validaciones_email (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL, codigo TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                usado INTEGER DEFAULT 0
            )
        ''')

    # --- computers ---
    cursor.execute("PRAGMA table_info(computers)")
    comp_cols = [c[1] for c in cursor.fetchall()]
    if not comp_cols:
        conn.execute('''
            CREATE TABLE computers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT, numero_serie TEXT,
                apellidos_nombre TEXT, notas TEXT,
                tipo TEXT, usuario TEXT, timestamp TEXT,
                proyecto TEXT DEFAULT 'Mitie'
            )
        ''')
    else:
        if 'proyecto' not in comp_cols:
            conn.execute("ALTER TABLE computers ADD COLUMN proyecto TEXT DEFAULT 'Mitie'")

    # --- incidencias ---
    cursor.execute("PRAGMA table_info(incidencias)")
    if not cursor.fetchall():
        conn.execute('''
            CREATE TABLE incidencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imei TEXT, usuario TEXT, telefono TEXT,
                notas TEXT, archivo_nombre TEXT,
                archivo_contenido BLOB, timestamp TEXT
            )
        ''')

    # --- usuarios ---
    cursor.execute("PRAGMA table_info(usuarios)")
    user_cols = [c[1] for c in cursor.fetchall()]
    if not user_cols:
        conn.execute('''
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                rol TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                fecha_creacion TEXT, notas TEXT
            )
        ''')
        pw = generate_password_hash('admin123')
        conn.execute(
            'INSERT INTO usuarios (username, password, rol, activo, fecha_creacion) VALUES (?,?,?,?,?)',
            ('admin', pw, 'admin', 1, datetime.utcnow().isoformat()),
        )
    else:
        if 'notas' not in user_cols:
            conn.execute('ALTER TABLE usuarios ADD COLUMN notas TEXT')

    # --- usuarios_gtd_sgpmr ---
    cursor.execute("PRAGMA table_info(usuarios_gtd_sgpmr)")
    if not cursor.fetchall():
        conn.execute('''
            CREATE TABLE usuarios_gtd_sgpmr (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_gtd TEXT, usuario_sgpmr TEXT,
                nombre_apellidos TEXT NOT NULL,
                correo_electronico TEXT, dni_nie TEXT,
                fecha_creacion TEXT
            )
        ''')

    # --- inventario_telefonos ---
    cursor.execute("PRAGMA table_info(inventario_telefonos)")
    if not cursor.fetchall():
        conn.execute('''
            CREATE TABLE inventario_telefonos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imei TEXT NOT NULL, numero_serie TEXT,
                modelo TEXT, telefono_asociado TEXT,
                fecha_creacion TEXT
            )
        ''')

    # --- datos_usuario ---
    cursor.execute("PRAGMA table_info(datos_usuario)")
    datos_cols = [c[1] for c in cursor.fetchall()]
    if not datos_cols:
        conn.execute('''
            CREATE TABLE datos_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dni TEXT NOT NULL,
                apellidos_nombre TEXT NOT NULL,
                telefono_personal TEXT,
                email_personal TEXT,
                email_corp TEXT,
                notas TEXT,
                fecha_creacion TEXT
            )
        ''')
    else:
        if 'notas' not in datos_cols:
            conn.execute("ALTER TABLE datos_usuario ADD COLUMN notas TEXT")

    # --- Índices para consultas frecuentes ---
    conn.execute('CREATE INDEX IF NOT EXISTS idx_entregas_imei ON entregas(imei)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_entregas_tipo ON entregas(tipo)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_entregas_timestamp ON entregas(timestamp)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_computers_tipo ON computers(tipo)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_computers_proyecto ON computers(proyecto)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_computers_timestamp ON computers(timestamp)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_incidencias_imei ON incidencias(imei)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_incidencias_timestamp ON incidencias(timestamp)')

    conn.commit()
    conn.close()
