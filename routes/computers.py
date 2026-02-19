"""Blueprint de computers: CRUD genérico que elimina la duplicación de rutas."""

from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import get_db
from routes._decorators import require_permission
from utils import parse_import_file, get_value

computers_bp = Blueprint('computers', __name__)

# ---------------------------------------------------------------------------
# Configuración de las variantes de computer
# Cada entrada mapea un endpoint → (tipo, proyecto, template, flash_ok)
# ---------------------------------------------------------------------------
_COMPUTER_VARIANTS = {
    'entrega_computer':         ('Entrega',    'Mitie', 'entrega_computer.html',         'Computer entregado correctamente'),
    'recepcion_computer':       ('Recepción',  'Mitie', 'recepcion_computer.html',       'Computer recibido correctamente'),
    'incidencias_computer':     ('Incidencia', 'Mitie', 'incidencias_computer.html',     'Incidencia registrada correctamente'),
    'Entrada_computer_aena':    ('Entrega',    'AENA',  'entrega_computer_aena.html',    'Computer AENA entregado correctamente'),
    'incidencias_computer_aena':('Incidencia', 'AENA',  'incidencias_computer_aena.html','Incidencia AENA registrada correctamente'),
}


def _computer_crud(tipo, proyecto, template, flash_msg):
    """Handler genérico GET/POST para registrar un computer."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        hostname = request.form.get('hostname', '').strip()
        numero_serie = request.form.get('numero_serie', '').strip()
        apellidos_nombre = request.form.get('apellidos_nombre', '').strip()
        notas = request.form.get('notas', '').strip()

        if not hostname:
            flash('Hostname es requerido', 'error')
            return render_template(template)

        db = get_db()
        db.execute(
            'INSERT INTO computers (hostname, numero_serie, apellidos_nombre, notas, tipo, usuario, timestamp, proyecto) '
            'VALUES (?,?,?,?,?,?,?,?)',
            (hostname, numero_serie, apellidos_nombre, notas, tipo,
             current_user.username, datetime.now().isoformat(), proyecto),
        )
        db.commit()
        flash(flash_msg, 'success')
        return redirect(url_for('main.index'))

    return render_template(template)


# Registrar las 5 rutas automáticamente
for _endpoint, (_tipo, _proyecto, _tpl, _msg) in _COMPUTER_VARIANTS.items():
    # Determinar la URL: normalmente /<endpoint>
    _url = f'/{_endpoint}'

    def _make_view(t=_tipo, p=_proyecto, tpl=_tpl, m=_msg):
        def view():
            return _computer_crud(t, p, tpl, m)
        return view

    computers_bp.add_url_rule(
        _url, endpoint=_endpoint,
        view_func=_make_view(),
        methods=['GET', 'POST'],
    )


# ---------------------------------------------------------------------------
# Editar computer
# ---------------------------------------------------------------------------

@computers_bp.route('/history_computers/<int:computer_id>/editar', methods=['GET', 'POST'])
@require_permission('administracion')
def editar_computer(computer_id):
    db = get_db()
    r = db.execute('SELECT * FROM computers WHERE id = ?', (computer_id,)).fetchone()
    if not r:
        flash('Registro no encontrado', 'error')
        return redirect(request.referrer or url_for('main.index'))

    if request.method == 'GET':
        return render_template('edit_computer.html', r=r)

    proyecto = request.form.get('proyecto', 'Mitie').strip()
    hostname = request.form.get('hostname', '').strip()
    numero_serie = request.form.get('numero_serie', '').strip()
    apellidos_nombre = request.form.get('apellidos_nombre', '').strip()
    notas = request.form.get('notas', '').strip()
    tipo = request.form.get('tipo', 'Entrega').strip()

    db.execute('''
        UPDATE computers SET proyecto=?, hostname=?, numero_serie=?, apellidos_nombre=?, notas=?, tipo=?
        WHERE id=?
    ''', (proyecto, hostname, numero_serie, apellidos_nombre, notas, tipo, computer_id))
    db.commit()
    flash('Registro actualizado correctamente', 'success')

    redirect_map = {
        'Entrega': 'history.history_computers_entrega',
        'Recepción': 'history.history_computers_recepcion',
    }
    return redirect(url_for(redirect_map.get(tipo, 'history.history_computers_incidencias')))


# ---------------------------------------------------------------------------
# Importar computers (usa parser genérico)
# ---------------------------------------------------------------------------

@computers_bp.route('/history_computers/import', methods=['GET', 'POST'])
@require_permission('registrar')
def import_computers():
    if request.method == 'GET':
        return render_template('import_computers.html')

    file = request.files.get('file')
    rows, errors = parse_import_file(file)
    if errors and not rows:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('computers.import_computers'))

    inserted = 0
    db = get_db()
    # Tipos de operación válidos
    _TIPOS_VALIDOS = {'entrega', 'recepción', 'recepcion', 'incidencia'}
    for r in rows:
        proyecto = get_value(r, ['proyecto', 'PROYECTO']) or 'Mitie'
        hostname = get_value(r, ['hostname', 'HOSTNAME', 'equipo'])
        numero_serie = get_value(r, ['numero_serie', 'serial', 'sn', 'SN'])
        apellidos_nombre = get_value(r, ['apellidos_nombre', 'persona', 'usuario_equipo'])
        notas = get_value(r, ['notas', 'observaciones'])
        tipo_raw = get_value(r, ['tipo', 'TIPO']) or 'Entrega'
        # Normalizar tipo: si no es un tipo de operación válido, usar 'Entrega'
        tipo = tipo_raw.strip()
        if tipo.lower() not in _TIPOS_VALIDOS:
            tipo = 'Entrega'
        else:
            # Normalizar la capitalización
            tipo_map = {'entrega': 'Entrega', 'recepción': 'Recepción', 'recepcion': 'Recepción', 'incidencia': 'Incidencia'}
            tipo = tipo_map.get(tipo.lower(), 'Entrega')

        if not hostname:
            errors.append('Fila sin hostname omitida.')
            continue

        try:
            db.execute(
                'INSERT INTO computers (hostname, numero_serie, apellidos_nombre, notas, tipo, usuario, timestamp, proyecto) '
                'VALUES (?,?,?,?,?,?,?,?)',
                (hostname, numero_serie, apellidos_nombre, notas, tipo,
                 current_user.username, datetime.now().isoformat(), proyecto),
            )
            inserted += 1
        except Exception as e:
            errors.append(f'Error insertando equipo {hostname}: {e}')
    db.commit()

    flash(f'Se insertaron {inserted} registros de computers.', 'success' if inserted else 'warning')
    for err in errors[:5]:
        flash(err, 'error')
    return redirect(url_for('history.history_computers_entrega'))
