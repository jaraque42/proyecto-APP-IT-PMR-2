"""Blueprint de autenticación: login, logout, perfil, cambiar contraseña."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import get_db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Usuario y contraseña requeridos', 'error')
            return redirect(url_for('auth.login'))

        db = get_db()
        usuario = db.execute(
            'SELECT id, username, password, rol, activo FROM usuarios WHERE username = ?',
            (username,),
        ).fetchone()

        if usuario and usuario['activo'] == 1 and check_password_hash(usuario['password'], password):
            user = User(usuario['id'], usuario['username'], usuario['rol'])
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/verificar_password_borrado', methods=['POST'])
@login_required
def verificar_password_borrado():
    data = request.get_json()
    password = data.get('password')
    if not password:
        return {'success': False, 'message': 'Contraseña requerida'}, 400

    db = get_db()
    row = db.execute('SELECT password FROM usuarios WHERE id = ?', (current_user.id,)).fetchone()
    if row and check_password_hash(row['password'], password):
        return {'success': True}
    return {'success': False, 'message': 'Contraseña incorrecta'}


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    db = get_db()
    if request.method == 'POST':
        notas = request.form.get('notas', '').strip()
        db.execute('UPDATE usuarios SET notas = ? WHERE id = ?', (notas, current_user.id))
        db.commit()
        flash('Notas actualizadas correctamente', 'success')
        return redirect(url_for('auth.perfil'))

    usuario = db.execute(
        'SELECT id, username, rol, notas, fecha_creacion FROM usuarios WHERE id = ?',
        (current_user.id,),
    ).fetchone()
    return render_template('perfil.html', usuario=usuario)


@auth_bp.route('/perfil/cambiar_contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    db = get_db()
    if request.method == 'POST':
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if not current_pw or not new_pw or not confirm:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('auth.cambiar_contrasena'))

        if new_pw != confirm:
            flash('La nueva contraseña y la confirmación no coinciden', 'error')
            return redirect(url_for('auth.cambiar_contrasena'))

        row = db.execute('SELECT password FROM usuarios WHERE id = ?', (current_user.id,)).fetchone()
        if not row:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('main.index'))

        stored_hash = row['password']
        if not check_password_hash(stored_hash, current_pw):
            flash('Contraseña actual incorrecta', 'error')
            return redirect(url_for('auth.cambiar_contrasena'))

        if len(new_pw) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('auth.cambiar_contrasena'))

        db.execute('UPDATE usuarios SET password = ? WHERE id = ?',
                   (generate_password_hash(new_pw), current_user.id))
        db.commit()
        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('auth.perfil'))

    return render_template('cambiar_contrasena.html')
