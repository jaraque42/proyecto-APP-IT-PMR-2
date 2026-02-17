"""Blueprint principal: dashboard / index."""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from models import get_db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    db = get_db()
    count_entregas_moviles = db.execute(
        "SELECT COUNT(*) FROM entregas WHERE LOWER(tipo) LIKE 'entrega%'"
    ).fetchone()[0]
    count_entregas_comp = db.execute(
        "SELECT COUNT(*) FROM computers WHERE tipo = 'Entrega'"
    ).fetchone()[0]
    total_entregas = count_entregas_moviles + count_entregas_comp

    count_incidencias_moviles = db.execute("SELECT COUNT(*) FROM incidencias").fetchone()[0]
    count_incidencias_comp = db.execute(
        "SELECT COUNT(*) FROM computers WHERE tipo = 'Incidencia'"
    ).fetchone()[0]
    total_incidencias = count_incidencias_moviles + count_incidencias_comp

    return render_template('index.html',
                           total_entregas=total_entregas,
                           total_incidencias=total_incidencias)
