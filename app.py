"""APP-IT-PMR-2  —  Aplicación Flask modular con Blueprints.

El monolito original se ha dividido en:
    models.py          – User, get_db, init_db
    utils.py           – helpers compartidos (PDF, email, importación, paginación)
    routes/            – Blueprints (auth, admin, main, moviles, computers,
                         history, incidents, extras)
"""

import os
import warnings

from dotenv import load_dotenv
from flask import Flask, jsonify, request as flask_request, redirect, url_for
from flask_login import LoginManager

from models import get_db, close_db, init_db, User
from routes import register_blueprints

# ---------------------------------------------------------------------------
# Cargar variables de entorno
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Crear aplicación Flask
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-in-production')
if app.secret_key == 'dev-only-change-in-production':
    warnings.warn(
        '⚠️  SECRET_KEY no configurada — usando valor por defecto INSEGURO. '
        'Configura SECRET_KEY en .env',
        stacklevel=1,
    )

# ---------------------------------------------------------------------------
# Flask-Login
# ---------------------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión'


@login_manager.unauthorized_handler
def unauthorized():
    """Devolver JSON 401 para peticiones AJAX/API; redirect normal para el resto."""
    if (flask_request.accept_mimetypes.best == 'application/json'
            or flask_request.path.startswith('/api/')):
        return jsonify(success=False, message='Sesión expirada. Inicia sesión de nuevo.'), 401
    return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    row = db.execute(
        'SELECT id, username, rol FROM usuarios WHERE id = ? AND activo = 1',
        (user_id,),
    ).fetchone()
    if row:
        return User(row['id'], row['username'], row['rol'])
    return None


# ---------------------------------------------------------------------------
# Ciclo de vida
# ---------------------------------------------------------------------------
app.teardown_appcontext(close_db)

# ---------------------------------------------------------------------------
# Inicializar BD y registrar blueprints
# ---------------------------------------------------------------------------
init_db()
register_blueprints(app)


# ---------------------------------------------------------------------------
# Ejecución directa (desarrollo)
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

