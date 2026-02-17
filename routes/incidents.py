"""Blueprint de incidencias."""

import io
import re
import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required

from models import get_db
from routes._decorators import require_permission
from utils import (
    paginate_query, build_excel, verify_delete_password,
    format_phone, is_valid_imei,
)

incidents_bp = Blueprint('incidents', __name__)


@incidents_bp.route('/incidents')
@require_permission('ver_incidencias')
def incidents():
    imei_search = request.args.get('imei', '').strip()
    usuario_search = request.args.get('usuario', '').strip()
    fecha_inicio = request.args.get('fecha_inicio', '').strip()
    fecha_fin = request.args.get('fecha_fin', '').strip()

    query = 'SELECT * FROM incidencias WHERE 1=1'
    params = []
    if imei_search:
        query += ' AND imei LIKE ?'; params.append(f'%{imei_search}%')
    if usuario_search:
        query += ' AND usuario LIKE ?'; params.append(f'%{usuario_search}%')
    if fecha_inicio:
        query += ' AND timestamp >= ?'; params.append(f'{fecha_inicio}T00:00:00')
    if fecha_fin:
        query += ' AND timestamp <= ?'; params.append(f'{fecha_fin}T23:59:59')
    query += ' ORDER BY timestamp DESC'

    db = get_db()
    pag = paginate_query(db, query, params)
    return render_template('incidents.html', incidents=pag['rows'],
                           page=pag['page'], total_pages=pag['total_pages'], total=pag['total'],
                           imei_search=imei_search, usuario_search=usuario_search,
                           fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@incidents_bp.route('/incidencia/<int:inc_id>/editar', methods=['GET', 'POST'])
@require_permission('administracion')
def editar_incidencia(inc_id):
    db = get_db()
    i = db.execute('SELECT * FROM incidencias WHERE id = ?', (inc_id,)).fetchone()
    if not i:
        flash('Incidencia no encontrada', 'error')
        return redirect(url_for('incidents.incidents'))

    if request.method == 'GET':
        return render_template('edit_incidencia.html', i=i)

    imei_raw = request.form.get('imei', '').strip()
    usuario = request.form.get('usuario', '').strip()
    raw_tel = request.form.get('telefono', '').strip()
    notas = request.form.get('notas', '').strip()

    imei_digits = re.sub(r'\D', '', imei_raw or '')
    if imei_raw and not is_valid_imei(imei_digits):
        flash('IMEI inválido — debe contener exactamente 15 dígitos', 'error')
        return redirect(url_for('incidents.editar_incidencia', inc_id=inc_id))

    telefono = format_phone(raw_tel)
    if raw_tel and telefono is None:
        flash('Teléfono inválido — debe ser numérico de 9 dígitos o con prefijo +34/0034/34', 'error')
        return redirect(url_for('incidents.editar_incidencia', inc_id=inc_id))

    db.execute('UPDATE incidencias SET imei=?, usuario=?, telefono=?, notas=? WHERE id=?',
               (imei_digits, usuario, telefono, notas, inc_id))
    db.commit()
    flash('Incidencia actualizada correctamente', 'success')
    return redirect(url_for('incidents.incidents'))


@incidents_bp.route('/incidents/export')
@require_permission('ver_incidencias')
def export_incidents():
    db = get_db()
    ids_param = request.args.get('ids', '').strip()
    imei_search = request.args.get('imei', '').strip()
    usuario_search = request.args.get('usuario', '').strip()

    if ids_param:
        id_list = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        if not id_list:
            rows = []
        else:
            ph = ','.join(['?'] * len(id_list))
            rows = db.execute(
                f'SELECT id, imei, usuario, telefono, notas, archivo_nombre, timestamp FROM incidencias WHERE id IN ({ph}) ORDER BY timestamp DESC',
                id_list,
            ).fetchall()
    else:
        query = 'SELECT id, imei, usuario, telefono, notas, archivo_nombre, timestamp FROM incidencias WHERE 1=1'
        params = []
        if imei_search:
            query += ' AND imei LIKE ?'; params.append(f'%{imei_search}%')
        if usuario_search:
            query += ' AND usuario LIKE ?'; params.append(f'%{usuario_search}%')
        query += ' ORDER BY timestamp DESC'
        rows = db.execute(query, params).fetchall()

    data = [[
        r['imei'] or '', r['usuario'] or '', r['telefono'] or '',
        r['notas'] or '', r['archivo_nombre'] or '', r['timestamp'] or '',
    ] for r in rows]

    bio = build_excel(['IMEI', 'Usuario', 'Teléfono', 'Notas', 'Archivo', 'Fecha (UTC)'], data)
    return send_file(bio, as_attachment=True, download_name='incidencias.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@incidents_bp.route('/incidents/delete-selected', methods=['POST'])
@require_permission('borrar_registros')
def delete_selected_incidents():
    password = request.form.get('password', '').strip()
    ids_param = request.form.get('ids', '').strip()

    if not verify_delete_password(password):
        flash('Contraseña incorrecta', 'error')
        return redirect(url_for('incidents.incidents'))

    if ids_param:
        id_list = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        if id_list:
            db = get_db()
            ph = ','.join(['?'] * len(id_list))
            db.execute(f'DELETE FROM incidencias WHERE id IN ({ph})', id_list)
            db.commit()

    return redirect(url_for('incidents.incidents'))


@incidents_bp.route('/incidents/download/<int:incident_id>')
@require_permission('ver_incidencias')
def download_incident_file(incident_id):
    db = get_db()
    incident = db.execute('SELECT * FROM incidencias WHERE id = ?', (incident_id,)).fetchone()
    if not incident:
        return "Incidencia no encontrada", 404

    return send_file(
        io.BytesIO(incident['archivo_contenido']),
        as_attachment=True,
        download_name=incident['archivo_nombre'],
    )
