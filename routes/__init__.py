"""Registro de blueprints."""

from .auth import auth_bp
from .admin import admin_bp
from .main import main_bp
from .moviles import moviles_bp
from .computers import computers_bp
from .history import history_bp
from .incidents import incidents_bp
from .extras import extras_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(moviles_bp)
    app.register_blueprint(computers_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(extras_bp)
