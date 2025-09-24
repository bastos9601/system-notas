from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui_cambiar_en_produccion')
# Configuración de base de datos
database_url = os.environ.get('DATABASE_URL', 'sqlite:///sistema_notas.db')

# Si es PostgreSQL (producción), convertir la URL si es necesario
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Función auxiliar para limpiar mensajes flash
def clear_flash_messages():
    """Limpia todos los mensajes flash de la sesión"""
    get_flashed_messages()

# Context processor para limpiar mensajes flash automáticamente
@app.context_processor
def inject_flash_cleanup():
    """Limpia mensajes flash duplicados automáticamente"""
    return dict()

# Modelos de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'admin' o 'docente'
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    ciclo = db.Column(db.String(20), nullable=False)  # primero, segundo, tercero, cuarto, quinto, sexto
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    docente = db.relationship('Usuario', backref=db.backref('materias', lazy=True))

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    tipo_evaluacion = db.Column(db.String(50), nullable=False)  # 'parcial', 'final', 'trabajo', etc.
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text)
    
    alumno = db.relationship('Alumno', backref=db.backref('notas', lazy=True))
    materia = db.relationship('Materia', backref=db.backref('notas', lazy=True))

# Rutas principales
@app.route('/', methods=['GET', 'POST'])
def index():
    alumno = None
    notas = None
    
    if request.method == 'POST':
        dni = request.form['dni']
        alumno = Alumno.query.filter_by(dni=dni).first()
        
        if alumno:
            # Consulta que incluye información del docente
            notas = db.session.query(Nota, Materia, Usuario).join(Materia, Nota.materia_id == Materia.id).join(Usuario, Materia.docente_id == Usuario.id).filter(Nota.alumno_id == alumno.id).all()
            
            # Guardar en sesión para mostrar después del redirect
            session['mostrar_resultados'] = True
            session['alumno_data'] = {
                'nombre': alumno.nombre,
                'apellido': alumno.apellido,
                'dni': alumno.dni,
                'email': alumno.email,
                'telefono': alumno.telefono,
                'ciclo': alumno.ciclo
            }
            session['notas_data'] = [
                {
                    'materia_nombre': materia.nombre,
                    'docente_username': docente.username,
                    'tipo_evaluacion': nota.tipo_evaluacion,
                    'nota': nota.nota,
                    'fecha': nota.fecha.strftime('%d/%m/%Y'),
                    'observaciones': nota.observaciones
                }
                for nota, materia, docente in notas
            ]
        else:
            flash('No se encontró un alumno con ese DNI', 'error')
        
        # Redirect para evitar reenvío
        return redirect(url_for('index'))
    
    # En GET, verificar si hay datos en sesión
    if session.get('mostrar_resultados'):
        # Crear objeto alumno temporal
        class AlumnoTemp:
            def __init__(self, data):
                self.nombre = data['nombre']
                self.apellido = data['apellido']
                self.dni = data['dni']
                self.email = data['email']
                self.telefono = data['telefono']
                self.ciclo = data['ciclo']
        
        alumno = AlumnoTemp(session['alumno_data'])
        notas = session['notas_data']
        
        # Limpiar sesión
        session.pop('mostrar_resultados', None)
        session.pop('alumno_data', None)
        session.pop('notas_data', None)
    
    return render_template('index.html', alumno=alumno, notas=notas)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and check_password_hash(usuario.password_hash, password):
            session['user_id'] = usuario.id
            session['username'] = usuario.username
            session['tipo'] = usuario.tipo
            
            if usuario.tipo == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('docente_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    usuarios = Usuario.query.all()
    alumnos = Alumno.query.all()
    materias = Materia.query.all()
    
    # Agregar contador de notas a cada materia para el dashboard
    materias_con_notas = []
    for materia in materias:
        notas_count = Nota.query.filter_by(materia_id=materia.id).count()
        materias_con_notas.append((materia, notas_count))
    
    return render_template('admin/dashboard.html', usuarios=usuarios, alumnos=alumnos, materias=materias_con_notas)

@app.route('/admin/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        tipo = request.form['tipo']
        
        try:
            if Usuario.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'error')
            elif Usuario.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
            else:
                usuario = Usuario(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    tipo=tipo
                )
                db.session.add(usuario)
                db.session.commit()
                flash('Usuario creado exitosamente', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: usuario.email' in str(e):
                flash('El email ya está registrado', 'error')
            elif 'UNIQUE constraint failed: usuario.username' in str(e):
                flash('El nombre de usuario ya existe', 'error')
            else:
                flash('Error al crear el usuario. Inténtalo de nuevo.', 'error')
                print(f"Error al crear usuario: {e}")
    
    return render_template('admin/crear_usuario.html')

@app.route('/admin/ver_notas')
def admin_ver_notas():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    # Obtener todas las notas con información de alumno y materia
    notas = db.session.query(Nota, Alumno, Materia).join(Alumno).join(Materia).order_by(Nota.fecha.desc()).all()
    
    return render_template('admin/ver_notas.html', notas=notas)

@app.route('/admin/ver_alumnos')
def admin_ver_alumnos():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    # Obtener todos los alumnos ordenados por fecha de registro
    alumnos = Alumno.query.order_by(Alumno.fecha_registro.desc()).all()
    
    return render_template('admin/ver_alumnos.html', alumnos=alumnos)

@app.route('/admin/ver_usuarios')
def admin_ver_usuarios():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    # Obtener todos los usuarios ordenados por fecha de creación
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    
    return render_template('admin/ver_usuarios.html', usuarios=usuarios)

@app.route('/admin/ver_materias')
def admin_ver_materias():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    # Obtener todas las materias con información del docente
    materias_query = db.session.query(Materia, Usuario).join(Usuario, Materia.docente_id == Usuario.id).order_by(Materia.id.desc()).all()
    
    # Crear una lista con información adicional de notas
    materias = []
    for materia, docente in materias_query:
        # Contar las notas para esta materia
        notas_count = Nota.query.filter_by(materia_id=materia.id).count()
        materias.append((materia, docente, notas_count))
    
    return render_template('admin/ver_materias.html', materias=materias)

@app.route('/admin/registrar_alumno', methods=['GET', 'POST'])
def registrar_alumno():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        ciclo = request.form['ciclo']
        
        try:
            if Alumno.query.filter_by(dni=dni).first():
                flash('Ya existe un alumno con ese DNI', 'error')
            else:
                alumno = Alumno(
                    dni=dni,
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    telefono=telefono,
                    fecha_nacimiento=datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date() if fecha_nacimiento else None,
                    ciclo=ciclo
                )
                db.session.add(alumno)
                db.session.commit()
                flash('Alumno registrado exitosamente', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: alumno.dni' in str(e):
                flash('Ya existe un alumno con ese DNI', 'error')
            else:
                flash('Error al registrar el alumno. Inténtalo de nuevo.', 'error')
                print(f"Error al registrar alumno: {e}")
    
    return render_template('admin/registrar_alumno.html')

@app.route('/admin/editar_alumno/<int:alumno_id>', methods=['GET', 'POST'])
def editar_alumno(alumno_id):
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    alumno = Alumno.query.get_or_404(alumno_id)
    
    if request.method == 'POST':
        try:
            alumno.dni = request.form['dni']
            alumno.nombre = request.form['nombre']
            alumno.apellido = request.form['apellido']
            alumno.email = request.form.get('email')
            alumno.telefono = request.form.get('telefono')
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            alumno.ciclo = request.form['ciclo']
            
            if fecha_nacimiento:
                alumno.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            else:
                alumno.fecha_nacimiento = None
            
            # Verificar si el DNI ya existe en otro alumno
            alumno_existente = Alumno.query.filter(Alumno.dni == alumno.dni, Alumno.id != alumno_id).first()
            if alumno_existente:
                flash('Ya existe otro alumno con ese DNI', 'error')
            else:
                db.session.commit()
                flash('Alumno actualizado exitosamente', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el alumno. Inténtalo de nuevo.', 'error')
            print(f"Error al editar alumno: {e}")
    
    return render_template('admin/editar_alumno.html', alumno=alumno)

@app.route('/admin/eliminar_alumno/<int:alumno_id>', methods=['POST'])
def eliminar_alumno(alumno_id):
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
        alumno = Alumno.query.get_or_404(alumno_id)
        
        # Eliminar todas las notas del alumno primero
        Nota.query.filter_by(alumno_id=alumno_id).delete()
        
        # Eliminar el alumno
        db.session.delete(alumno)
        db.session.commit()
        
        flash('Alumno eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el alumno. Inténtalo de nuevo.', 'error')
        print(f"Error al eliminar alumno: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/eliminar_usuario/<int:usuario_id>', methods=['POST'])
def eliminar_usuario(usuario_id):
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # No permitir eliminar el propio usuario admin
        if usuario.id == session['user_id']:
            flash('No puedes eliminar tu propio usuario', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Si es un docente, eliminar sus materias primero
        if usuario.tipo == 'docente':
            # Eliminar todas las notas de las materias del docente
            materias_docente = Materia.query.filter_by(docente_id=usuario_id).all()
            for materia in materias_docente:
                Nota.query.filter_by(materia_id=materia.id).delete()
            
            # Eliminar las materias del docente
            Materia.query.filter_by(docente_id=usuario_id).delete()
        
        # Eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        
        flash('Usuario eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el usuario. Inténtalo de nuevo.', 'error')
        print(f"Error al eliminar usuario: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        try:
            usuario.username = request.form['username']
            usuario.email = request.form['email']
            usuario.tipo = request.form['tipo']
            
            # Solo cambiar contraseña si se proporciona una nueva
            nueva_password = request.form.get('password')
            if nueva_password and nueva_password.strip():
                usuario.password_hash = generate_password_hash(nueva_password)
            
            # Verificar si el username ya existe en otro usuario
            usuario_existente = Usuario.query.filter(Usuario.username == usuario.username, Usuario.id != usuario_id).first()
            if usuario_existente:
                flash('Ya existe otro usuario con ese nombre de usuario', 'error')
            else:
                db.session.commit()
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el usuario. Inténtalo de nuevo.', 'error')
            print(f"Error al editar usuario: {e}")
    
    return render_template('admin/editar_usuario.html', usuario=usuario)

@app.route('/admin/crear_materia', methods=['GET', 'POST'])
def admin_crear_materia():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        codigo = request.form['codigo']
        docente_id = request.form['docente_id']
        
        # Validar que los campos no estén vacíos
        if not nombre.strip() or not codigo.strip() or not docente_id:
            flash('Por favor, completa todos los campos requeridos', 'error')
            return render_template('admin/crear_materia.html', docentes=Usuario.query.filter_by(tipo='docente').all())
        
        # Verificar si ya existe una materia con ese código
        materia_existente = Materia.query.filter_by(codigo=codigo).first()
        if materia_existente:
            flash('Ya existe una materia con ese código', 'error')
            return render_template('admin/crear_materia.html', docentes=Usuario.query.filter_by(tipo='docente').all())
        
        # Verificar que el docente existe
        docente = Usuario.query.filter_by(id=docente_id, tipo='docente').first()
        if not docente:
            flash('El docente seleccionado no es válido', 'error')
            return render_template('admin/crear_materia.html', docentes=Usuario.query.filter_by(tipo='docente').all())
        
        try:
            # Crear la nueva materia
            materia = Materia(
                nombre=nombre.strip(),
                codigo=codigo.strip(),
                docente_id=docente_id
            )
            db.session.add(materia)
            db.session.commit()
            flash('Materia creada exitosamente', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: materia.codigo' in str(e):
                flash('Ya existe una materia con ese código', 'error')
            else:
                flash('Error al crear la materia. Inténtalo de nuevo.', 'error')
                print(f"Error al crear materia: {e}")
    
    docentes = Usuario.query.filter_by(tipo='docente').all()
    return render_template('admin/crear_materia.html', docentes=docentes)

@app.route('/admin/editar_materia/<int:materia_id>', methods=['GET', 'POST'])
def admin_editar_materia(materia_id):
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    materia = Materia.query.get_or_404(materia_id)
    
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            codigo = request.form['codigo']
            docente_id = request.form['docente_id']
            
            # Verificar si el código ya existe en otra materia
            materia_existente = Materia.query.filter(Materia.codigo == codigo, Materia.id != materia_id).first()
            if materia_existente:
                flash('Ya existe otra materia con ese código', 'error')
            else:
                # Verificar que el docente existe
                docente = Usuario.query.filter_by(id=docente_id, tipo='docente').first()
                if not docente:
                    flash('El docente seleccionado no es válido', 'error')
                else:
                    materia.nombre = nombre
                    materia.codigo = codigo
                    materia.docente_id = docente_id
                    db.session.commit()
                    flash('Materia actualizada exitosamente', 'success')
                    return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la materia. Inténtalo de nuevo.', 'error')
            print(f"Error al editar materia: {e}")
    
    docentes = Usuario.query.filter_by(tipo='docente').all()
    return render_template('admin/editar_materia.html', materia=materia, docentes=docentes)

@app.route('/admin/eliminar_materia/<int:materia_id>', methods=['POST'])
def admin_eliminar_materia(materia_id):
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
        materia = Materia.query.get_or_404(materia_id)
        
        # Eliminar todas las notas de la materia primero
        Nota.query.filter_by(materia_id=materia_id).delete()
        
        # Eliminar la materia
        db.session.delete(materia)
        db.session.commit()
        
        flash('Materia eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la materia. Inténtalo de nuevo.', 'error')
        print(f"Error al eliminar materia: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/docente/dashboard')
def docente_dashboard():
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    materias = Materia.query.filter_by(docente_id=docente_id).all()
    alumnos = Alumno.query.all()
    
    return render_template('docente/dashboard.html', materias=materias, alumnos=alumnos)

@app.route('/docente/agregar_nota', methods=['GET', 'POST'])
def agregar_nota():
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    materias = Materia.query.filter_by(docente_id=docente_id).all()
    alumnos = Alumno.query.all()
    
    if request.method == 'POST':
        alumno_id = request.form['alumno_id']
        materia_id = request.form['materia_id']
        nota = float(request.form['nota'])
        tipo_evaluacion = request.form['tipo_evaluacion']
        observaciones = request.form.get('observaciones')
        
        # Verificar que la materia pertenece al docente
        materia = Materia.query.filter_by(id=materia_id, docente_id=docente_id).first()
        if not materia:
            flash('No tienes permisos para agregar notas a esta materia', 'error')
            return redirect(url_for('agregar_nota'))
        
        nueva_nota = Nota(
            alumno_id=alumno_id,
            materia_id=materia_id,
            nota=nota,
            tipo_evaluacion=tipo_evaluacion,
            observaciones=observaciones
        )
        db.session.add(nueva_nota)
        db.session.commit()
        flash('Nota agregada exitosamente', 'success')
        return redirect(url_for('docente_dashboard'))
    
    return render_template('docente/agregar_nota.html', materias=materias, alumnos=alumnos)

@app.route('/docente/ver_notas')
def docente_ver_notas():
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    # Obtener las notas de las materias del docente
    notas = db.session.query(Nota, Alumno, Materia).join(Alumno).join(Materia).filter(Materia.docente_id == docente_id).order_by(Nota.fecha.desc()).all()
    
    return render_template('docente/ver_notas.html', notas=notas)

@app.route('/docente/editar_nota/<int:nota_id>', methods=['GET', 'POST'])
def editar_nota(nota_id):
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    
    # Obtener la nota y verificar que pertenece a una materia del docente
    nota = db.session.query(Nota, Materia).join(Materia).filter(Nota.id == nota_id, Materia.docente_id == docente_id).first()
    
    if not nota:
        flash('Nota no encontrada o no tienes permisos para editarla', 'error')
        return redirect(url_for('docente_ver_notas'))
    
    nota_obj, materia = nota
    
    if request.method == 'POST':
        try:
            nueva_nota = float(request.form['nota'])
            tipo_evaluacion = request.form['tipo_evaluacion']
            observaciones = request.form.get('observaciones')
            
            # Validar que la nota esté en el rango correcto
            if nueva_nota < 0 or nueva_nota > 20:
                flash('La nota debe estar entre 0 y 20', 'error')
            else:
                nota_obj.nota = nueva_nota
                nota_obj.tipo_evaluacion = tipo_evaluacion
                nota_obj.observaciones = observaciones
                
                db.session.commit()
                flash('Nota actualizada exitosamente', 'success')
                return redirect(url_for('docente_ver_notas'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la nota. Inténtalo de nuevo.', 'error')
            print(f"Error al editar nota: {e}")
    
    return render_template('docente/editar_nota.html', nota=nota_obj, materia=materia)

@app.route('/docente/eliminar_nota/<int:nota_id>', methods=['POST'])
def eliminar_nota(nota_id):
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    
    # Obtener la nota y verificar que pertenece a una materia del docente
    nota = db.session.query(Nota, Materia).join(Materia).filter(Nota.id == nota_id, Materia.docente_id == docente_id).first()
    
    if not nota:
        flash('Nota no encontrada o no tienes permisos para eliminarla', 'error')
        return redirect(url_for('docente_ver_notas'))
    
    nota_obj, materia = nota
    
    try:
        db.session.delete(nota_obj)
        db.session.commit()
        flash('Nota eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la nota. Inténtalo de nuevo.', 'error')
        print(f"Error al eliminar nota: {e}")
    
    return redirect(url_for('docente_ver_notas'))

@app.route('/docente/ver_alumnos')
def docente_ver_alumnos():
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    # Obtener todos los alumnos ordenados por fecha de registro
    alumnos = Alumno.query.order_by(Alumno.fecha_registro.desc()).all()
    
    return render_template('docente/ver_alumnos.html', alumnos=alumnos)

@app.route('/docente/ver_materias')
def docente_ver_materias():
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    # Obtener todas las materias del docente
    materias = Materia.query.filter_by(docente_id=docente_id).order_by(Materia.id.desc()).all()
    
    # Agregar contador de notas a cada materia
    materias_con_notas = []
    for materia in materias:
        notas_count = Nota.query.filter_by(materia_id=materia.id).count()
        materias_con_notas.append((materia, notas_count))
    
    return render_template('docente/ver_materias.html', materias=materias_con_notas)

@app.route('/docente/ver_notas_materia/<int:materia_id>')
def docente_ver_notas_materia(materia_id):
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    
    # Verificar que la materia pertenece al docente
    materia = Materia.query.filter_by(id=materia_id, docente_id=docente_id).first()
    if not materia:
        flash('Materia no encontrada o no tienes permisos para verla', 'error')
        return redirect(url_for('docente_ver_materias'))
    
    # Obtener las notas de la materia específica con información del alumno
    notas = db.session.query(Nota, Alumno).join(Alumno).filter(Nota.materia_id == materia_id).order_by(Nota.fecha.desc()).all()
    
    # Actualizar notas que no tengan tipo_evaluacion
    for nota, alumno in notas:
        if not nota.tipo_evaluacion or nota.tipo_evaluacion.strip() == '':
            nota.tipo_evaluacion = 'Parcial'  # Valor por defecto
            db.session.commit()
    
    return render_template('docente/ver_notas_materia.html', materia=materia, notas=notas)

@app.route('/admin/actualizar_tipos_evaluacion')
def actualizar_tipos_evaluacion():
    """Ruta para actualizar todas las notas que no tengan tipo de evaluación"""
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
        # Buscar todas las notas que no tengan tipo_evaluacion o esté vacío
        notas_sin_tipo = Nota.query.filter(
            (Nota.tipo_evaluacion == None) | 
            (Nota.tipo_evaluacion == '') | 
            (Nota.tipo_evaluacion == 'None')
        ).all()
        
        contador = 0
        for nota in notas_sin_tipo:
            nota.tipo_evaluacion = 'Parcial'  # Valor por defecto
            contador += 1
        
        db.session.commit()
        
        if contador > 0:
            flash(f'Se actualizaron {contador} notas con tipo de evaluación por defecto', 'success')
        else:
            flash('Todas las notas ya tienen tipo de evaluación asignado', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar los tipos de evaluación', 'error')
        print(f"Error al actualizar tipos de evaluación: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/ver_notas_alumno/<int:alumno_id>')
def admin_ver_notas_alumno(alumno_id):
    """Ver todas las notas de un alumno específico"""
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
        # Obtener el alumno
        alumno = Alumno.query.get_or_404(alumno_id)
        
        # Obtener todas las notas del alumno
        notas_query = Nota.query.filter_by(alumno_id=alumno_id).order_by(Nota.fecha.desc()).all()
        
        # Crear una lista con información adicional
        notas = []
        for nota in notas_query:
            # Asegurar que tipo_evaluacion no sea None
            if not nota.tipo_evaluacion or nota.tipo_evaluacion.strip() == '':
                nota.tipo_evaluacion = 'Parcial'
                db.session.commit()
            
            materia = Materia.query.get(nota.materia_id)
            docente = Usuario.query.get(materia.docente_id) if materia else None
            notas.append((nota, materia, docente))
        
        return render_template('admin/ver_notas_alumno.html', alumno=alumno, notas=notas)
        
    except Exception as e:
        print(f"Error en admin_ver_notas_alumno: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar las notas del alumno', 'error')
        return redirect(url_for('admin_ver_alumnos'))


# Inicializar base de datos y usuario admin
def init_db():
    """Inicializar base de datos y crear usuario admin si no existe"""
    with app.app_context():
        db.create_all()
        
        # Crear usuario administrador por defecto si no existe
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(
                username='admin',
                email='admin@sistema.com',
                password_hash=generate_password_hash('admin123'),
                tipo='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado: admin / admin123")
    
# Inicializar la base de datos al importar el módulo
init_db()

if __name__ == '__main__':
    # Configuración para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
