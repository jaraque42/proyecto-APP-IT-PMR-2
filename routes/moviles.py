"""Blueprint de operaciones con móviles: entrega, recepción, incidencia + API OTP."""

import random
import re

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from models import get_db
from routes._decorators import require_permission
from utils import (
    format_phone, is_mitie_email, is_valid_imei,
    generate_entrega_pdf, send_validation_email_verbose,
)

moviles_bp = Blueprint('moviles', __name__)


# ---------------------------------------------------------------------------
# Páginas de formulario (GET)
# ---------------------------------------------------------------------------

@moviles_bp.route('/entrega_moviles')
@login_required
def entrega_moviles():
    return render_template('entrega_moviles.html')


@moviles_bp.route('/recepcion_moviles')
@login_required
def recepcion_moviles():
    return render_template('recepcion_moviles.html')


@moviles_bp.route('/incidencias_moviles')
@login_required
def incidencias_moviles():
    return render_template('incidencias_moviles.html')


# ---------------------------------------------------------------------------
# API de validación por email (OTP)
# ---------------------------------------------------------------------------

@moviles_bp.route('/api/send_email_otp', methods=['POST'])
@login_required
def api_send_email_otp():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify(success=False, message='No se recibieron datos JSON'), 400

        email = (data.get('email') or '').strip()
        if not email or '@' not in email:
            return jsonify(success=False, message='Email inválido'), 400

        codigo = f"{random.randint(100000, 999999)}"
        db = get_db()
        db.execute('INSERT INTO validaciones_email (email, codigo) VALUES (?, ?)', (email, codigo))
        db.commit()

        result = send_validation_email_verbose(email, codigo)
        if result['success']:
            return jsonify(success=True)
        return jsonify(success=False, message=f"Error al enviar email: {result.get('error', 'desconocido')}"), 500
    except Exception as exc:
        return jsonify(success=False, message=f'Error interno: {exc}'), 500


@moviles_bp.route('/api/verify_email_otp', methods=['POST'])
@login_required
def api_verify_email_otp():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify(success=False, message='No se recibieron datos JSON'), 400

        email = (data.get('email') or '').strip()
        codigo = (data.get('codigo') or '').strip()

        db = get_db()
        row = db.execute('''
            SELECT id FROM validaciones_email
            WHERE email = ? AND codigo = ? AND usado = 0
            AND timestamp >= datetime('now', '-30 minutes')
            ORDER BY timestamp DESC LIMIT 1
        ''', (email, codigo)).fetchone()

        if row:
            db.execute('UPDATE validaciones_email SET usado = 1 WHERE id = ?', (row['id'],))
            db.commit()
            return jsonify(success=True)

        return jsonify(success=False, message='Código incorrecto o expirado'), 400
    except Exception as exc:
        return jsonify(success=False, message=f'Error interno: {exc}'), 500


# ---------------------------------------------------------------------------
# POST: registrar entrega / recepción / incidencia
# ---------------------------------------------------------------------------

def _validate_movil_fields(situm, imei_raw, raw_telefono):
    """Valida campos comunes. Retorna (imei_digits, telefono, error_msg) o error_msg como str."""
    errors = []

    if situm and not is_mitie_email(situm):
        errors.append('El campo Situm debe ser un email con dominio @mitie.es')

    imei_digits = re.sub(r'\D', '', imei_raw or '')
    if imei_raw and not is_valid_imei(imei_digits):
        errors.append('IMEI inválido — debe contener exactamente 15 dígitos')

    telefono = format_phone(raw_telefono)
    if raw_telefono and telefono is None:
        errors.append('Teléfono inválido — debe ser numérico de 9 dígitos sin prefijo 34')

    if errors:
        return None, None, errors
    return imei_digits, telefono, []


@moviles_bp.route('/entrega', methods=['POST'])
@require_permission('registrar')
def entrega():
    situm = request.form.get('situm', '').strip()
    usuario = request.form.get('usuario', '').strip()
    imei_raw = request.form.get('imei', '').strip()
    raw_telefono = request.form.get('telefono', '').strip()
    notas_telefono = request.form.get('notas_telefono', '').strip()
    email_usuario = request.form.get('email_usuario', '').strip()
    codigo_otp = request.form.get('codigo_otp', '').strip()
    timestamp = datetime.utcnow().isoformat()

    imei, telefono, errors = _validate_movil_fields(situm, imei_raw, raw_telefono)
    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('main.index'))

    db = get_db()

    # Comprobar si el IMEI ya está entregado sin recepcionar
    if imei:
        last = db.execute(
            'SELECT tipo FROM entregas WHERE imei = ? ORDER BY timestamp DESC LIMIT 1', (imei,)
        ).fetchone()
        if last and last['tipo'] == 'entrega':
            flash(f'No se puede registrar la entrega: el dispositivo con IMEI {imei} no ha sido recepcionado aún.', 'error')
            return redirect(url_for('main.index'))

    db.execute(
        'INSERT INTO entregas (situm, usuario, imei, telefono, notas_telefono, tipo, timestamp, codigo_validacion, email_usuario) VALUES (?,?,?,?,?,?,?,?,?)',
        (situm, usuario, imei, telefono, notas_telefono, 'entrega', timestamp, codigo_otp, email_usuario),
    )
    db.commit()

    pdf_buffer, pdf_filename = generate_entrega_pdf(situm, usuario, imei, telefono, notas_telefono, timestamp, codigo_otp)
    return send_file(pdf_buffer, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')


@moviles_bp.route('/recepcion', methods=['POST'])
@require_permission('registrar')
def recepcion():
    situm = request.form.get('situm', '').strip()
    usuario = request.form.get('usuario', '').strip()
    imei_raw = request.form.get('imei', '').strip()
    raw_telefono = request.form.get('telefono', '').strip()
    notas_telefono = request.form.get('notas_telefono', '').strip()
    timestamp = datetime.utcnow().isoformat()

    imei, telefono, errors = _validate_movil_fields(situm, imei_raw, raw_telefono)
    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('main.index'))

    db = get_db()
    db.execute(
        'INSERT INTO entregas (situm, usuario, imei, telefono, notas_telefono, tipo, timestamp) VALUES (?,?,?,?,?,?,?)',
        (situm, usuario, imei, telefono, notas_telefono, 'recepcion', timestamp),
    )
    db.commit()
    return redirect(url_for('main.index'))


@moviles_bp.route('/incidencia', methods=['POST'])
@require_permission('registrar')
def incidencia():
    usuario = request.form.get('usuario', '').strip()
    imei_raw = request.form.get('imei', '').strip()
    raw_telefono = request.form.get('telefono', '').strip()
    notas = request.form.get('notas', '').strip()
    timestamp = datetime.utcnow().isoformat()

    imei, telefono, errors = _validate_movil_fields('', imei_raw, raw_telefono)
    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('main.index'))

    archivo_nombre = None
    archivo_contenido = None
    if 'archivo' in request.files and request.files['archivo'].filename != '':
        archivo = request.files['archivo']
        allowed = {'pdf', 'jpg', 'jpeg'}
        if '.' not in archivo.filename or archivo.filename.rsplit('.', 1)[1].lower() not in allowed:
            return redirect(url_for('main.index') + '?error=Invalid file type')
        archivo_contenido = archivo.read()
        archivo_nombre = archivo.filename

    db = get_db()
    db.execute(
        'INSERT INTO incidencias (imei, usuario, telefono, notas, archivo_nombre, archivo_contenido, timestamp) VALUES (?,?,?,?,?,?,?)',
        (imei, usuario, telefono, notas, archivo_nombre, archivo_contenido, timestamp),
    )
    db.commit()
    return redirect(url_for('main.index'))
