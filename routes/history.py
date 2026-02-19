"""Blueprint de histórico: vistas paginadas, exportación y borrado."""

import re
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required

from models import get_db
from routes._decorators import require_permission
from utils import (
    paginate_query, build_excel, verify_delete_password,
    format_phone, is_mitie_email, is_valid_imei,
    parse_import_file, get_value,
)

history_bp = Blueprint('history', __name__)


# ===================================================================
# Helpers internos
# ===================================================================

def _search_params_moviles():
    """Extrae parámetros de búsqueda comunes para entregas/recepciones."""
    return {
        'imei_search':    request.args.get('imei', '').strip(),
        'usuario_search': request.args.get('usuario', '').strip(),
        'fecha_inicio':   request.args.get('fecha_inicio', '').strip(),
        'fecha_fin':      request.args.get('fecha_fin', '').strip(),
    }


def _build_entregas_query(tipos, search):
    """Construye query + params para buscar en tabla entregas filtrado por tipos."""
    tipo_placeholders = ','.join(['?' for _ in tipos])
    query = f'SELECT * FROM entregas WHERE LOWER(tipo) IN ({tipo_placeholders})'
    params = list(tipos)

    if search['imei_search']:
        query += ' AND imei LIKE ?'
        params.append(f"%{search['imei_search']}%")
    if search['usuario_search']:
        query += ' AND usuario LIKE ?'
        params.append(f"%{search['usuario_search']}%")
    if search['fecha_inicio']:
        query += ' AND timestamp >= ?'
        params.append(f"{search['fecha_inicio']}T00:00:00")
    if search['fecha_fin']:
        query += ' AND timestamp <= ?'
        params.append(f"{search['fecha_fin']}T23:59:59")

    query += ' ORDER BY timestamp DESC'
    return query, params


def _build_computers_query(tipo):
    """Construye query + params para el histórico de computers."""
    hostname_search = request.args.get('hostname', '').strip()
    sn_search = request.args.get('sn', '').strip()
    proyecto_filter = request.args.get('proyecto', '').strip()

    query = 'SELECT * FROM computers WHERE tipo = ?'
    params = [tipo]

    if hostname_search:
        query += ' AND hostname LIKE ?'
        params.append(f'%{hostname_search}%')
    if sn_search:
        query += ' AND numero_serie LIKE ?'
        params.append(f'%{sn_search}%')
    if proyecto_filter:
        query += ' AND proyecto = ?'
        params.append(proyecto_filter)

    query += ' ORDER BY timestamp DESC'
    return query, params, hostname_search, sn_search, proyecto_filter


# ===================================================================
# Histórico entregas móviles
# ===================================================================

@history_bp.route('/history')
@require_permission('ver_historico')
def history():
    return redirect(url_for('history.history_entrega'))


@history_bp.route('/history_entrega')
@require_permission('ver_historico')
def history_entrega():
    search = _search_params_moviles()
    query, params = _build_entregas_query(['entrega', 'entregas'], search)
    db = get_db()
    pag = paginate_query(db, query, params)
    return render_template('history_entrega.html', **pag, **search)


@history_bp.route('/history_recepcion')
@require_permission('ver_historico')
def history_recepcion():
    search = _search_params_moviles()
    query, params = _build_entregas_query(['recepción', 'recepcion', 'recepciones'], search)
    db = get_db()
    pag = paginate_query(db, query, params)
    return render_template('history_recepcion.html', **pag, **search)


# ===================================================================
# Histórico computers (genérico)
# ===================================================================

def _render_computers_history(tipo, title_prefix):
    query, params, hostname_search, sn_search, proyecto_filter = _build_computers_query(tipo)
    db = get_db()
    pag = paginate_query(db, query, params)
    display_title = f"{title_prefix} {'- ' + proyecto_filter if proyecto_filter else ''}"
    return render_template(
        'history_computers.html', **pag,
        title=display_title,
        hostname_search=hostname_search,
        sn_search=sn_search,
        proyecto_filter=proyecto_filter,
        tipo_actual=tipo,
    )


@history_bp.route('/history_computers_entrega')
@require_permission('ver_historico')
def history_computers_entrega():
    return _render_computers_history('Entrega', 'Histórico Entregas Computer')


@history_bp.route('/history_computers_recepcion')
@require_permission('ver_historico')
def history_computers_recepcion():
    return _render_computers_history('Recepción', 'Histórico Recepciones Computer')


@history_bp.route('/history_computers_incidencias')
@require_permission('ver_historico')
def history_computers_incidencias():
    return _render_computers_history('Incidencia', 'Histórico Incidencias Computer')


# ===================================================================
# Exportar
# ===================================================================

@history_bp.route('/history/export')
@require_permission('ver_historico')
def export_history():
    return redirect(url_for('history.export_history_entrega'))


@history_bp.route('/history_entrega/export')
@require_permission('ver_historico')
def export_history_entrega():
    db = get_db()
    ids_param = request.args.get('ids', '').strip()
    search = _search_params_moviles()

    if ids_param:
        id_list = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        if not id_list:
            rows = []
        else:
            ph = ','.join(['?'] * len(id_list))
            rows = db.execute(
                f'SELECT * FROM entregas WHERE LOWER(tipo) IN ("entrega","entregas") AND id IN ({ph}) ORDER BY timestamp DESC',
                id_list,
            ).fetchall()
    else:
        query, params = _build_entregas_query(['entrega', 'entregas'], search)
        # Remove the SELECT * and replace for export (still works with *)
        rows = db.execute(query, params).fetchall()

    data = [[
        r['situm'] or '', r['usuario'] or '', r['imei'] or '', r['telefono'] or '',
        r['email_usuario'] or '', r['codigo_validacion'] or 'Sin firma', r['timestamp'] or '',
    ] for r in rows]

    bio = build_excel(['Situm', 'Usuario', 'IMEI', 'Teléfono', 'Email', 'Firma', 'Fecha (UTC)'], data)
    return send_file(bio, as_attachment=True, download_name='historico_entregas.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@history_bp.route('/history_recepcion/export')
@require_permission('ver_historico')
def export_history_recepcion():
    db = get_db()
    ids_param = request.args.get('ids', '').strip()
    search = _search_params_moviles()

    if ids_param:
        id_list = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        if not id_list:
            rows = []
        else:
            ph = ','.join(['?'] * len(id_list))
            rows = db.execute(
                f'SELECT * FROM entregas WHERE LOWER(tipo) IN ("recepción","recepcion","recepciones") AND id IN ({ph}) ORDER BY timestamp DESC',
                id_list,
            ).fetchall()
    else:
        query, params = _build_entregas_query(['recepción', 'recepcion', 'recepciones'], search)
        rows = db.execute(query, params).fetchall()

    data = [[
        r['situm'] or '', r['usuario'] or '', r['imei'] or '', r['telefono'] or '',
        r['notas_telefono'] or '', r['timestamp'] or '',
    ] for r in rows]

    bio = build_excel(['Situm', 'Usuario', 'IMEI', 'Teléfono', 'Notas de Teléfono', 'Fecha (UTC)'], data)
    return send_file(bio, as_attachment=True, download_name='historico_recepciones.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@history_bp.route('/history_computers/export')
@require_permission('ver_historico')
def export_history_computers():
    db = get_db()
    hostname_search = request.args.get('hostname', '').strip()
    sn_search = request.args.get('sn', '').strip()
    proyecto_filter = request.args.get('proyecto', '').strip()
    tipo_filter = request.args.get('tipo', '').strip()

    query = 'SELECT proyecto, hostname, numero_serie, apellidos_nombre, notas, usuario, timestamp, tipo FROM computers WHERE 1=1'
    params = []
    if tipo_filter:
        query += ' AND tipo = ?'; params.append(tipo_filter)
    if hostname_search:
        query += ' AND hostname LIKE ?'; params.append(f'%{hostname_search}%')
    if sn_search:
        query += ' AND numero_serie LIKE ?'; params.append(f'%{sn_search}%')
    if proyecto_filter:
        query += ' AND proyecto = ?'; params.append(proyecto_filter)
    query += ' ORDER BY timestamp DESC'

    rows = db.execute(query, params).fetchall()
    data = [[
        r['proyecto'] or 'Mitie', r['hostname'] or '', r['numero_serie'] or '',
        r['apellidos_nombre'] or '', r['notas'] or '', r['usuario'] or '',
        r['timestamp'] or '', r['tipo'] or '',
    ] for r in rows]

    bio = build_excel(['Proyecto', 'Hostname', 'S/N', 'Persona', 'Notas', 'Registrado por', 'Fecha', 'Tipo'], data)
    filename = f"historico_computers_{tipo_filter or 'todos'}.xlsx"
    return send_file(bio, as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ===================================================================
# Borrado
# ===================================================================

@history_bp.route('/history/clear', methods=['POST'])
@require_permission('borrar_registros')
def clear_history():
    password = request.form.get('password', '').strip()
    if not verify_delete_password(password):
        flash('Contraseña incorrecta', 'error')
        return redirect(url_for('history.history_entrega'))

    db = get_db()
    db.execute('DELETE FROM entregas')
    db.commit()
    return redirect(url_for('history.history_entrega'))


def _delete_selected_entregas(tipos, redirect_endpoint):
    """Borrar registros seleccionados de la tabla entregas."""
    password = request.form.get('password', '').strip()
    ids_param = request.form.get('ids', '').strip()

    if not verify_delete_password(password):
        flash('Contraseña incorrecta', 'error')
        return redirect(url_for(redirect_endpoint))

    if ids_param:
        id_list = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        if id_list:
            db = get_db()
            ph_ids = ','.join(['?'] * len(id_list))
            ph_tipos = ','.join(['?'] * len(tipos))
            db.execute(
                f'DELETE FROM entregas WHERE id IN ({ph_ids}) AND LOWER(tipo) IN ({ph_tipos})',
                id_list + list(tipos),
            )
            db.commit()

    return redirect(url_for(redirect_endpoint))


@history_bp.route('/history/delete-selected', methods=['POST'])
@require_permission('borrar_registros')
def delete_selected():
    return _delete_selected_entregas(['entrega', 'entregas'], 'history.history_entrega')


@history_bp.route('/history_entrega/delete-selected', methods=['POST'])
@require_permission('borrar_registros')
def delete_selected_entrega():
    return _delete_selected_entregas(['entrega', 'entregas'], 'history.history_entrega')


@history_bp.route('/history_recepcion/delete-selected', methods=['POST'])
@require_permission('borrar_registros')
def delete_selected_recepcion():
    return _delete_selected_entregas(['recepcion', 'recepción', 'recepciones'], 'history.history_recepcion')


@history_bp.route('/history_computers/delete-selected', methods=['POST'])
@require_permission('borrar_registros')
def delete_selected_computers():
    password = request.form.get('password', '').strip()
    ids_param = request.form.get('ids', '').strip()

    if not verify_delete_password(password):
        flash('Contraseña incorrecta', 'error')
        return redirect(request.referrer or url_for('main.index'))

    if ids_param:
        id_list = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        if id_list:
            db = get_db()
            ph = ','.join(['?'] * len(id_list))
            db.execute(f'DELETE FROM computers WHERE id IN ({ph})', id_list)
            db.commit()

    return redirect(request.referrer or url_for('main.index'))


# ===================================================================
# Editar registros de entregas
# ===================================================================

@history_bp.route('/registro/<int:registro_id>/editar', methods=['GET', 'POST'])
@require_permission('administracion')
def editar_registro(registro_id):
    db = get_db()
    r = db.execute('SELECT * FROM entregas WHERE id = ?', (registro_id,)).fetchone()
    if not r:
        flash('Registro no encontrado', 'error')
        return redirect(url_for('history.history'))

    if request.method == 'GET':
        return render_template('edit_entrega.html', r=r)

    situm = request.form.get('situm', '').strip()
    usuario = request.form.get('usuario', '').strip()
    imei_raw = request.form.get('imei', '').strip()
    raw_tel = request.form.get('telefono', '').strip()
    notas_telefono = request.form.get('notas_telefono', '').strip()

    if situm and not is_mitie_email(situm):
        flash('El campo Situm debe ser un email con dominio @mitie.es', 'error')
        return redirect(url_for('history.editar_registro', registro_id=registro_id))

    imei_digits = re.sub(r'\D', '', imei_raw or '')
    if imei_raw and not is_valid_imei(imei_digits):
        flash('IMEI inválido — debe contener exactamente 15 dígitos', 'error')
        return redirect(url_for('history.editar_registro', registro_id=registro_id))

    telefono = format_phone(raw_tel)
    if raw_tel and telefono is None:
        flash('Teléfono inválido — debe ser numérico de 9 dígitos o con prefijo +34/0034/34', 'error')
        return redirect(url_for('history.editar_registro', registro_id=registro_id))

    db.execute(
        'UPDATE entregas SET situm=?, usuario=?, imei=?, telefono=?, notas_telefono=? WHERE id=?',
        (situm, usuario, imei_digits, telefono, notas_telefono, registro_id),
    )
    db.commit()
    flash('Registro actualizado correctamente', 'success')
    return redirect(url_for('history.history'))


# ===================================================================
# Importar entregas móviles (usa parser genérico)
# ===================================================================

@history_bp.route('/import', methods=['GET', 'POST'])
@require_permission('registrar')
def import_file():
    if request.method == 'GET':
        return render_template('import.html')

    file = request.files.get('file')
    rows, errors = parse_import_file(file)

    inserted = 0
    if rows:
        db = get_db()
        for r in rows:
            situm = get_value(r, ['situm', 'SITUM'])
            usuario = get_value(r, ['usuario', 'user', 'nombre'])
            imei = get_value(r, ['imei', 'IMEI'])
            raw_tel = get_value(r, ['telefono', 'phone', 'telefono_movil']) or ''
            telefono = format_phone(raw_tel)
            if raw_tel and telefono is None:
                errors.append(f'Fila con IMEI={imei}: teléfono inválido "{raw_tel}"')
                continue
            notas_telefono = get_value(r, ['notas_telefono', 'notas', 'notes', 'modelo', 'model'])
            tipo = get_value(r, ['tipo', 'type']) or 'entrega'
            try:
                db.execute(
                    'INSERT INTO entregas (situm, usuario, imei, telefono, notas_telefono, tipo, timestamp) VALUES (?,?,?,?,?,?,?)',
                    (situm, usuario, imei, telefono, notas_telefono, tipo, datetime.utcnow().isoformat()),
                )
                inserted += 1
            except Exception as e:
                errors.append(f'Error insertando fila con IMEI={imei}: {e}')
        db.commit()

    return render_template('import_result.html', inserted=inserted, errors=errors)
