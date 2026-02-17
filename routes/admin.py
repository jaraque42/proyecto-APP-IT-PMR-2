"""Blueprint de administración de usuarios."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import sqlite3

from models import get_db, ROLES_PERMISOS
from routes._decorators import require_permission

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/administracion')
@require_permission('administracion')
def administracion():
    db = get_db()
    usuarios = db.execute(
        'SELECT id, username, rol, activo, fecha_creacion FROM usuarios ORDER BY fecha_creacion DESC'
    ).fetchall()
    return render_template('administracion.html', usuarios=usuarios, roles=ROLES_PERMISOS.keys())


@admin_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@require_permission('crear_usuario')
def crear_usuario():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        rol = request.form.get('rol', 'viewer')

        if not username or not password:
            flash('Usuario y contraseña requeridos', 'error')
            return redirect(url_for('admin.crear_usuario'))

        if rol not in ROLES_PERMISOS:
            flash('Rol inválido', 'error')
            return redirect(url_for('admin.crear_usuario'))

        db = get_db()
        try:
            db.execute(
                'INSERT INTO usuarios (username, password, rol, activo, fecha_creacion) VALUES (?,?,?,?,?)',
                (username, generate_password_hash(password), rol, 1, datetime.utcnow().isoformat()),
            )
            db.commit()
            flash(f'Usuario {username} creado correctamente', 'success')
            return redirect(url_for('admin.administracion'))
        except sqlite3.IntegrityError:
            flash(f'El usuario {username} ya existe', 'error')
            return redirect(url_for('admin.crear_usuario'))

    return render_template('crear_usuario.html', roles=ROLES_PERMISOS.keys())


@admin_bp.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@require_permission('cambiar_rol')
def editar_usuario(usuario_id):
    db = get_db()
    usuario = db.execute('SELECT id, username, rol, activo FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin.administracion'))

    if request.method == 'POST':
        rol = request.form.get('rol', 'viewer')
        activo = request.form.get('activo', '0')
        if rol not in ROLES_PERMISOS:
            flash('Rol inválido', 'error')
            return redirect(url_for('admin.editar_usuario', usuario_id=usuario_id))

        db.execute('UPDATE usuarios SET rol = ?, activo = ? WHERE id = ?',
                   (rol, 1 if activo == '1' else 0, usuario_id))
        db.commit()
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('admin.administracion'))

    return render_template('editar_usuario.html', usuario=usuario,
                           roles=ROLES_PERMISOS.keys(), roles_permisos=ROLES_PERMISOS)


@admin_bp.route('/usuarios/<int:usuario_id>/cambiar_contrasena', methods=['GET', 'POST'])
@require_permission('cambiar_rol')
def cambiar_contrasena_usuario(usuario_id):
    db = get_db()
    usuario = db.execute('SELECT id, username FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin.administracion'))

    if request.method == 'POST':
        new_pw = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if not new_pw or not confirm:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('admin.cambiar_contrasena_usuario', usuario_id=usuario_id))
        if new_pw != confirm:
            flash('La nueva contraseña y la confirmación no coinciden', 'error')
            return redirect(url_for('admin.cambiar_contrasena_usuario', usuario_id=usuario_id))

        db.execute('UPDATE usuarios SET password = ? WHERE id = ?',
                   (generate_password_hash(new_pw), usuario_id))
        db.commit()
        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('admin.administracion'))

    return render_template('admin_cambiar_contrasena.html',
                           usuario_id=usuario_id, username=usuario['username'])


@admin_bp.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@require_permission('eliminar_usuario')
def eliminar_usuario(usuario_id):
    if usuario_id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'error')
        return redirect(url_for('admin.administracion'))

    db = get_db()
    usuario = db.execute('SELECT username FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin.administracion'))

    db.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
    db.commit()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('admin.administracion'))
