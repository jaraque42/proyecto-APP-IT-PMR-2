"""Punto de entrada de la aplicación Flask.

Los scripts `start.bat` / `start.ps1` ejecutan `python app.py`. Este fichero
crea la app, inicializa la base de datos y registra los blueprints.
"""

from __future__ import annotations

import os
import warnings

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):  # type: ignore[no-redef]
        return False

from flask import Flask, jsonify, redirect, request as flask_request, url_for
from flask_login import LoginManager

from models import User, close_db, get_db, init_db
from routes import register_blueprints


def create_app() -> Flask:

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    if app.secret_key == "dev-only-change-in-production":
        warnings.warn(
            "⚠️  SECRET_KEY no configurada — usando valor por defecto INSEGURO. "
            "Configura SECRET_KEY en variables de entorno o en .env",
            stacklevel=1,
        )

    init_db()
    app.teardown_appcontext(close_db)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor inicia sesión"
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        if (
            flask_request.accept_mimetypes.best == "application/json"
            or flask_request.path.startswith("/api/")
        ):
            return (
                jsonify(success=False, message="Sesión expirada. Inicia sesión de nuevo."),
                401,
            )
        return redirect(url_for("auth.login"))

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        db = get_db()
        row = db.execute(
            "SELECT id, username, rol FROM usuarios WHERE id = ? AND activo = 1",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        return User(row["id"], row["username"], row["rol"])

    register_blueprints(app)
    return app


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
    app.run(host=host, port=port, debug=debug)
