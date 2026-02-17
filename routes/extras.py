"""Blueprint de extras: Usuarios GTD/SGPMR + Inventario de Teléfonos."""

import sqlite3
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from models import get_db
from routes._decorators import require_permission
from utils import parse_import_file, check_admin_password

extras_bp = Blueprint('extras', __name__)


# ===================================================================
# Usuarios GTD / SGPMR
# ===================================================================

@extras_bp.route('/usuarios_gtd_sgpmr')
@require_permission('registrar')
def usuarios_gtd_sgpmr():
    db = get_db()
    usuarios = db.execute('SELECT * FROM usuarios_gtd_sgpmr ORDER BY fecha_creacion DESC').fetchall()
    return render_template('usuarios_gtd_sgpmr.html', usuarios=usuarios)


@extras_bp.route('/usuarios_gtd_sgpmr/crear', methods=['GET', 'POST'])
@require_permission('registrar')
def crear_usuario_gtd_sgpmr():
    db = get_db()
    if request.method == 'POST':
        usuario_gtd = request.form.get('usuario_gtd', '').strip()
        usuario_sgpmr = request.form.get('usuario_sgpmr', '').strip()
        nombre_apellidos = request.form.get('nombre_apellidos', '').strip()
        correo_electronico = request.form.get('correo_electronico', '').strip()
        dni_nie = request.form.get('dni_nie', '').strip()

        if not nombre_apellidos:
            flash('El nombre y apellidos es requerido', 'error')
            return redirect(url_for('extras.crear_usuario_gtd_sgpmr'))

        try:
            db.execute('''
                INSERT INTO usuarios_gtd_sgpmr (usuario_gtd, usuario_sgpmr, nombre_apellidos, correo_electronico, dni_nie, fecha_creacion)
                VALUES (?,?,?,?,?,?)
            ''', (usuario_gtd or None, usuario_sgpmr or None, nombre_apellidos,
                  correo_electronico or None, dni_nie or None, datetime.utcnow().isoformat()))
            db.commit()
            flash('Usuario creado correctamente', 'success')
            return redirect(url_for('extras.usuarios_gtd_sgpmr'))
        except sqlite3.IntegrityError as e:
            flash(f'Error al crear usuario: {e}', 'error')
            return redirect(url_for('extras.crear_usuario_gtd_sgpmr'))

    return render_template('crear_usuario_gtd_sgpmr.html')


@extras_bp.route('/usuarios_gtd_sgpmr/<int:usuario_id>/editar', methods=['GET', 'POST'])
@require_permission('registrar')
def editar_usuario_gtd_sgpmr(usuario_id):
    db = get_db()
    usuario = db.execute('SELECT * FROM usuarios_gtd_sgpmr WHERE id = ?', (usuario_id,)).fetchone()
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('extras.usuarios_gtd_sgpmr'))

    if request.method == 'POST':
        usuario_gtd = request.form.get('usuario_gtd', '').strip()
        usuario_sgpmr = request.form.get('usuario_sgpmr', '').strip()
        nombre_apellidos = request.form.get('nombre_apellidos', '').strip()
        correo_electronico = request.form.get('correo_electronico', '').strip()
        dni_nie = request.form.get('dni_nie', '').strip()

        if not nombre_apellidos:
            flash('El nombre y apellidos es requerido', 'error')
            return redirect(url_for('extras.editar_usuario_gtd_sgpmr', usuario_id=usuario_id))

        try:
            db.execute('''
                UPDATE usuarios_gtd_sgpmr SET usuario_gtd=?, usuario_sgpmr=?, nombre_apellidos=?, correo_electronico=?, dni_nie=?
                WHERE id=?
            ''', (usuario_gtd or None, usuario_sgpmr or None, nombre_apellidos,
                  correo_electronico or None, dni_nie or None, usuario_id))
            db.commit()
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('extras.usuarios_gtd_sgpmr'))
        except sqlite3.IntegrityError as e:
            flash(f'Error al actualizar usuario: {e}', 'error')
            return redirect(url_for('extras.editar_usuario_gtd_sgpmr', usuario_id=usuario_id))

    return render_template('editar_usuario_gtd_sgpmr.html', usuario=usuario)


@extras_bp.route('/usuarios_gtd_sgpmr/<int:usuario_id>/eliminar', methods=['POST'])
@require_permission('registrar')
def eliminar_usuario_gtd_sgpmr(usuario_id):
    password = request.form.get('admin_password')
    if not check_admin_password(password):
        flash('Contraseña de administrador incorrecta', 'error')
        return redirect(url_for('extras.usuarios_gtd_sgpmr'))

    db = get_db()
    db.execute('DELETE FROM usuarios_gtd_sgpmr WHERE id = ?', (usuario_id,))
    db.commit()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('extras.usuarios_gtd_sgpmr'))


@extras_bp.route('/usuarios_gtd_sgpmr/importar', methods=['GET', 'POST'])
@require_permission('registrar')
def importar_usuarios_gtd_sgpmr():
    if request.method == 'GET':
        return render_template('importar_usuarios_gtd_sgpmr.html')

    archivo = request.files.get('archivo')
    rows, file_errors = parse_import_file(archivo)
    if file_errors and not rows:
        for e in file_errors:
            flash(e, 'error')
        return redirect(url_for('extras.importar_usuarios_gtd_sgpmr'))

    db = get_db()
    inserted = 0
    errors = list(file_errors)
    for idx, row in enumerate(rows, 2):
        try:
            nombre_apellidos = str(row.get('nombre_apellidos') or '').strip()
            if not nombre_apellidos:
                errors.append(f"Fila {idx}: nombre_apellidos es requerido")
                continue
            db.execute('''
                INSERT INTO usuarios_gtd_sgpmr (usuario_gtd, usuario_sgpmr, nombre_apellidos, correo_electronico, dni_nie, fecha_creacion)
                VALUES (?,?,?,?,?,?)
            ''', (
                str(row.get('usuario_gtd') or '').strip() or None,
                str(row.get('usuario_sgpmr') or '').strip() or None,
                nombre_apellidos,
                str(row.get('correo_electronico') or '').strip() or None,
                str(row.get('dni_nie') or '').strip() or None,
                datetime.utcnow().isoformat(),
            ))
            inserted += 1
        except sqlite3.IntegrityError as e:
            errors.append(f"Fila {idx}: {e}")
    db.commit()

    flash(f'Se importaron {inserted} usuarios correctamente. Errores: {len(errors)}',
          'success' if inserted else 'warning')
    for err in errors[:10]:
        flash(err, 'error')
    return redirect(url_for('extras.usuarios_gtd_sgpmr'))


# ===================================================================
# Inventario de Teléfonos
# ===================================================================

@extras_bp.route('/inventario_telefonos')
@require_permission('registrar')
def inventario_telefonos():
    db = get_db()
    telefonos = db.execute('SELECT * FROM inventario_telefonos ORDER BY fecha_creacion DESC').fetchall()
    return render_template('inventario_telefonos.html', telefonos=telefonos)


@extras_bp.route('/inventario_telefonos/crear', methods=['GET', 'POST'])
@require_permission('registrar')
def crear_inventario_telefonos():
    if request.method == 'POST':
        imei = request.form.get('imei', '').strip()
        numero_serie = request.form.get('numero_serie', '').strip()
        modelo = request.form.get('modelo', '').strip()
        telefono_asociado = request.form.get('telefono_asociado', '').strip()

        if not imei:
            flash('El IMEI es requerido', 'error')
            return redirect(url_for('extras.crear_inventario_telefonos'))

        db = get_db()
        try:
            db.execute('''
                INSERT INTO inventario_telefonos (imei, numero_serie, modelo, telefono_asociado, fecha_creacion)
                VALUES (?,?,?,?,?)
            ''', (imei, numero_serie or None, modelo or None, telefono_asociado or None,
                  datetime.utcnow().isoformat()))
            db.commit()
            flash('Teléfono registrado correctamente', 'success')
            return redirect(url_for('extras.inventario_telefonos'))
        except sqlite3.IntegrityError as e:
            flash(f'Error al registrar teléfono: {e}', 'error')
            return redirect(url_for('extras.crear_inventario_telefonos'))

    return render_template('crear_inventario_telefonos.html')


@extras_bp.route('/inventario_telefonos/<int:telefono_id>/editar', methods=['GET', 'POST'])
@require_permission('registrar')
def editar_inventario_telefonos(telefono_id):
    db = get_db()
    telefono = db.execute('SELECT * FROM inventario_telefonos WHERE id = ?', (telefono_id,)).fetchone()
    if not telefono:
        flash('Teléfono no encontrado', 'error')
        return redirect(url_for('extras.inventario_telefonos'))

    if request.method == 'POST':
        imei = request.form.get('imei', '').strip()
        numero_serie = request.form.get('numero_serie', '').strip()
        modelo = request.form.get('modelo', '').strip()
        telefono_asociado = request.form.get('telefono_asociado', '').strip()

        if not imei:
            flash('El IMEI es requerido', 'error')
            return redirect(url_for('extras.editar_inventario_telefonos', telefono_id=telefono_id))

        try:
            db.execute('''
                UPDATE inventario_telefonos SET imei=?, numero_serie=?, modelo=?, telefono_asociado=?
                WHERE id=?
            ''', (imei, numero_serie or None, modelo or None, telefono_asociado or None, telefono_id))
            db.commit()
            flash('Teléfono actualizado correctamente', 'success')
            return redirect(url_for('extras.inventario_telefonos'))
        except sqlite3.IntegrityError as e:
            flash(f'Error al actualizar teléfono: {e}', 'error')
            return redirect(url_for('extras.editar_inventario_telefonos', telefono_id=telefono_id))

    return render_template('editar_inventario_telefonos.html', telefono=telefono)


@extras_bp.route('/inventario_telefonos/<int:telefono_id>/eliminar', methods=['POST'])
@require_permission('registrar')
def eliminar_inventario_telefonos(telefono_id):
    password = request.form.get('admin_password')
    if not check_admin_password(password):
        flash('Contraseña de administrador incorrecta', 'error')
        return redirect(url_for('extras.inventario_telefonos'))

    db = get_db()
    db.execute('DELETE FROM inventario_telefonos WHERE id = ?', (telefono_id,))
    db.commit()
    flash('Teléfono eliminado correctamente', 'success')
    return redirect(url_for('extras.inventario_telefonos'))


@extras_bp.route('/inventario_telefonos/delete-selected', methods=['POST'])
@require_permission('registrar')
def delete_selected_inventario_telefonos():
    ids_param = request.form.get('ids', '').strip()
    password = request.form.get('admin_password')

    if not check_admin_password(password):
        flash('Contraseña de administrador incorrecta', 'error')
        return redirect(url_for('extras.inventario_telefonos'))

    if ids_param:
        id_list = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        if id_list:
            db = get_db()
            ph = ','.join(['?'] * len(id_list))
            db.execute(f'DELETE FROM inventario_telefonos WHERE id IN ({ph})', id_list)
            db.commit()
            flash('Teléfonos eliminados correctamente', 'success')

    return redirect(url_for('extras.inventario_telefonos'))


@extras_bp.route('/inventario_telefonos/importar', methods=['GET', 'POST'])
@require_permission('registrar')
def importar_inventario_telefonos():
    if request.method == 'GET':
        return render_template('importar_inventario_telefonos.html')

    archivo = request.files.get('archivo')
    rows, file_errors = parse_import_file(archivo)
    if file_errors and not rows:
        for e in file_errors:
            flash(e, 'error')
        return redirect(url_for('extras.importar_inventario_telefonos'))

    db = get_db()
    inserted = 0
    errors = list(file_errors)
    for idx, row in enumerate(rows, 2):
        try:
            imei = str(row.get('imei') or '').strip()
            if not imei:
                errors.append(f"Fila {idx}: IMEI es requerido")
                continue

            db.execute('''
                INSERT INTO inventario_telefonos (imei, numero_serie, modelo, telefono_asociado, fecha_creacion)
                VALUES (?,?,?,?,?)
            ''', (
                imei,
                str(row.get('numero_serie') or '').strip() or None,
                str(row.get('modelo') or '').strip() or None,
                str(row.get('telefono_asociado') or '').strip() or None,
                datetime.utcnow().isoformat(),
            ))
            inserted += 1
        except sqlite3.IntegrityError as e:
            errors.append(f"Fila {idx}: {e}")
    db.commit()

    flash(f'Se importaron {inserted} teléfonos correctamente. Errores: {len(errors)}',
          'success' if inserted else 'warning')
    for err in errors[:10]:
        flash(err, 'error')
    return redirect(url_for('extras.inventario_telefonos'))
