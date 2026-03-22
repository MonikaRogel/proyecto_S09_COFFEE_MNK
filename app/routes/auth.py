from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Usuario, Cliente   # Importamos Cliente
from ..extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("=== LLEGÓ A LOGIN ===")
    print("Método:", request.method)
    if request.method == 'POST':
        print("Datos POST recibidos:", request.form)
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Email: {email}")
        user = Usuario.query.filter_by(mail=email).first()
        print(f"Usuario encontrado: {user}")
        if user and user.check_password(password):
            print("Contraseña correcta")
            login_user(user)
            print("Usuario logueado")
            return redirect(url_for('main.home'))
        else:
            print("Credenciales inválidas")
            flash('Correo o contraseña incorrectos', 'error')
    return render_template('login.html', titulo='Iniciar Sesión')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    print("=== LLEGÓ A REGISTER ===")
    print("Método:", request.method)
    if request.method == 'POST':
        print("Datos POST recibidos:", request.form)
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Nombre: {nombre}, Email: {email}")
        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('auth.register'))
        if Usuario.query.filter_by(mail=email).first():
            flash('El correo ya está registrado', 'error')
            return redirect(url_for('auth.register'))
        # Crear usuario
        user = Usuario(nombre=nombre, mail=email, rol='cliente')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Para obtener id si fuera necesario
        # Crear cliente asociado
        cliente = Cliente(nombre=nombre, email=email)
        db.session.add(cliente)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('auth.login'))
    return render_template('registro.html', titulo='Registro')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('main.home'))