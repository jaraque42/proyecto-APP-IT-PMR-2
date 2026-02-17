"""Decoradores compartidos entre blueprints."""

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import login_required, current_user


def require_permission(permiso):
    """Decorador que exige un permiso específico del usuario autenticado."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.tiene_permiso(permiso):
                flash('No tienes permisos para realizar esta acción', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
