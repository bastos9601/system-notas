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

# Función auxiliar para convertir números de ciclo a texto
def convertir_ciclo_a_texto(ciclo):
    """Convierte números de ciclo a texto y normaliza a minúsculas"""
    if ciclo is None:
        return None
    
    # Convertir números a texto y normalizar
    ciclo_map = {
        '1': 'primero', '2': 'segundo', '3': 'tercero',
        '4': 'cuarto', '5': 'quinto', '6': 'sexto',
        'I': 'primero', 'II': 'segundo', 'III': 'tercero',
        'IV': 'cuarto', 'V': 'quinto', 'VI': 'sexto',
        'Primero': 'primero', 'Segundo': 'segundo', 'Tercero': 'tercero',
        'Cuarto': 'cuarto', 'Quinto': 'quinto', 'Sexto': 'sexto',
        'primero': 'primero', 'segundo': 'segundo', 'tercero': 'tercero',
        'cuarto': 'cuarto', 'quinto': 'quinto', 'sexto': 'sexto'
    }
    
    return ciclo_map.get(str(ciclo), str(ciclo).lower())

# Context processor para limpiar mensajes flash automáticamente
@app.context_processor
def inject_flash_cleanup():
    """Limpia mensajes flash duplicados automáticamente"""
    return {
        'clear_flash_messages': clear_flash_messages,
        'convertir_ciclo_a_texto': convertir_ciclo_a_texto
    }

# Modelos de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'admin', 'docente' o 'alumno'
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
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)  # Relación con Usuario
    usuario = db.relationship('Usuario', backref=db.backref('alumno', uselist=False))

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
@app.route('/')
def index():
    # Redirigir directamente al login
    return redirect(url_for('login'))



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
            elif usuario.tipo == 'docente':
                return redirect(url_for('docente_dashboard'))
            elif usuario.tipo == 'alumno':
                return redirect(url_for('alumno_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login_moderno.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
        # Obtener datos de forma segura
        usuarios = Usuario.query.all() or []
        alumnos = Alumno.query.all() or []
        materias = Materia.query.all() or []
        
        # Agregar contador de notas a cada materia para el dashboard
        materias_con_notas = []
        for materia in materias:
            try:
                notas_count = Nota.query.filter_by(materia_id=materia.id).count()
                materias_con_notas.append((materia, notas_count))
            except Exception as e:
                print(f"Error al contar notas para materia {materia.id}: {e}")
                materias_con_notas.append((materia, 0))
        
        return render_template('admin/dashboard_moderno.html', 
                             usuarios=usuarios, 
                             alumnos=alumnos, 
                             materias=materias_con_notas)
    
    except Exception as e:
        print(f"Error en admin_dashboard: {e}")
        # En caso de error, renderizar con datos vacíos
        return render_template('admin/dashboard_moderno.html', 
                             usuarios=[], 
                             alumnos=[], 
                             materias=[])

@app.route('/admin/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        tipo = request.form['tipo']
        alumno_id = request.form.get('alumno_id')  # Solo para tipo 'alumno'
        
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
                db.session.flush()  # Para obtener el ID del usuario
                
                # Si es un usuario de tipo alumno, asociarlo con el alumno
                if tipo == 'alumno' and alumno_id:
                    alumno = Alumno.query.get(alumno_id)
                    if alumno:
                        # Verificar que el alumno no tenga ya un usuario asociado
                        if alumno.usuario_id is None:
                            alumno.usuario_id = usuario.id
                        else:
                            flash('El alumno seleccionado ya tiene un usuario asociado', 'error')
                            db.session.rollback()
                            return render_template('admin/crear_usuario_moderno.html', alumnos=Alumno.query.filter_by(usuario_id=None).all())
                    else:
                        flash('El alumno seleccionado no existe', 'error')
                        db.session.rollback()
                        return render_template('admin/crear_usuario_moderno.html', alumnos=Alumno.query.filter_by(usuario_id=None).all())
                
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
    
    # Obtener alumnos que no tienen usuario asociado
    alumnos_sin_usuario = Alumno.query.filter_by(usuario_id=None).all()
    return render_template('admin/crear_usuario_moderno.html', alumnos=alumnos_sin_usuario)

@app.route('/admin/crear_usuario_alumno', methods=['GET', 'POST'])
def crear_usuario_alumno():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        alumno_id = request.form['alumno_id']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Verificar que el alumno existe y no tiene usuario
            alumno = Alumno.query.get(alumno_id)
            if not alumno:
                flash('El alumno seleccionado no existe', 'error')
            elif alumno.usuario_id is not None:
                flash('El alumno seleccionado ya tiene un usuario asociado', 'error')
            elif Usuario.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'error')
            elif Usuario.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
            else:
                # Crear el usuario
                usuario = Usuario(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    tipo='alumno'
                )
                db.session.add(usuario)
                db.session.flush()  # Para obtener el ID del usuario
                
                # Asociar el usuario con el alumno
                alumno.usuario_id = usuario.id
                
                db.session.commit()
                flash(f'Usuario creado exitosamente para {alumno.nombre} {alumno.apellido}', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: usuario.email' in str(e):
                flash('El email ya está registrado', 'error')
            elif 'UNIQUE constraint failed: usuario.username' in str(e):
                flash('El nombre de usuario ya existe', 'error')
            else:
                flash('Error al crear el usuario. Inténtalo de nuevo.', 'error')
                print(f"Error al crear usuario alumno: {e}")
    
    # Obtener alumnos que no tienen usuario asociado
    alumnos_sin_usuario = Alumno.query.filter_by(usuario_id=None).all()
    return render_template('admin/crear_usuario_alumno_moderno.html', alumnos=alumnos_sin_usuario)

@app.route('/admin/crear_docente', methods=['GET', 'POST'])
def crear_docente():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form.get('telefono')
        
        try:
            # Verificar que el username y email no existan
            if Usuario.query.filter_by(username=username).first():
                flash('El nombre de usuario ya existe', 'error')
            elif Usuario.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
            else:
                # Crear el usuario docente
                usuario = Usuario(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    tipo='docente',
                    nombre=nombre,
                    apellido=apellido,
                    telefono=telefono
                )
                
                db.session.add(usuario)
                db.session.commit()
                flash('Docente creado exitosamente', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: usuario.email' in str(e):
                flash('El email ya está registrado', 'error')
            elif 'UNIQUE constraint failed: usuario.username' in str(e):
                flash('El nombre de usuario ya existe', 'error')
            else:
                flash('Error al crear el docente. Inténtalo de nuevo.', 'error')
                print(f"Error al crear docente: {e}")
    
    return render_template('admin/crear_docente_moderno.html')

@app.route('/admin/ver_notas')
def admin_ver_notas():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
    # Obtener todas las notas con información de alumno y materia
        notas_query = db.session.query(Nota, Alumno, Materia, Usuario).select_from(Nota).outerjoin(Alumno, Nota.alumno_id == Alumno.id).outerjoin(Materia, Nota.materia_id == Materia.id).outerjoin(Usuario, Materia.docente_id == Usuario.id).order_by(Nota.fecha.desc()).all()
        
        # Crear una lista con objetos nota que tengan las relaciones cargadas
        notas = []
        for nota, alumno, materia, docente in notas_query:
            # Asignar las relaciones al objeto nota
            nota.alumno = alumno
            nota.materia = materia
            nota.materia.docente = docente
            
            # Formatear fecha
            if nota.fecha:
                nota.fecha_formatted = nota.fecha.strftime('%d/%m/%Y')
            else:
                nota.fecha_formatted = 'N/A'
            
            notas.append(nota)
        
        # Calcular estadísticas
        total_notas = len(notas)
        notas_aprobadas = len([n for n in notas if n.nota >= 13])
        notas_recuperacion = len([n for n in notas if 10 <= n.nota < 13])
        notas_desaprobadas = len([n for n in notas if 5 <= n.nota < 10])
        
        # Obtener materias y alumnos para los filtros
        materias = Materia.query.all()
        alumnos = Alumno.query.all()
        
        return render_template('admin/ver_notas_moderno.html', 
                             notas=notas, 
                             materias=materias, 
                             alumnos=alumnos,
                             total_notas=total_notas,
                             notas_aprobadas=notas_aprobadas,
                             notas_recuperacion=notas_recuperacion,
                             notas_desaprobadas=notas_desaprobadas)
    
    except Exception as e:
        print(f"Error en admin_ver_notas: {e}")
        # En caso de error, devolver listas vacías
        return render_template('admin/ver_notas_moderno.html', 
                             notas=[], 
                             materias=[], 
                             alumnos=[],
                             total_notas=0,
                             notas_aprobadas=0,
                             notas_recuperacion=0,
                             notas_desaprobadas=0)

@app.route('/admin/editar_materia/<int:materia_id>', methods=['GET', 'POST'])
def admin_editar_materia(materia_id):
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    # Obtener la materia
    materia = Materia.query.get_or_404(materia_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form['nombre'].strip()
            codigo = request.form['codigo'].strip()
            docente_id = request.form.get('docente_id')
            
            # Validaciones
            if not nombre or not codigo:
                flash('El nombre y código son obligatorios', 'error')
                return render_template('admin/editar_materia_moderno.html', materia=materia, docentes=docentes)
            
            # Verificar si el código ya existe en otra materia
            materia_existente = Materia.query.filter(Materia.codigo == codigo, Materia.id != materia_id).first()
            if materia_existente:
                flash('Ya existe una materia con ese código', 'error')
                return render_template('admin/editar_materia_moderno.html', materia=materia, docentes=docentes)
            
            # Actualizar la materia
            materia.nombre = nombre
            materia.codigo = codigo
            materia.docente_id = int(docente_id) if docente_id else None
            
            db.session.commit()
            flash('Materia actualizada exitosamente', 'success')
            return redirect(url_for('admin_ver_materias'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la materia. Inténtalo de nuevo.', 'error')
            print(f"Error al editar materia: {e}")
    
    # Obtener docentes para el formulario
    docentes = Usuario.query.filter_by(tipo='docente').all()
    
    return render_template('admin/editar_materia_moderno.html', materia=materia, docentes=docentes)

@app.route('/admin/ver_alumnos')
def admin_ver_alumnos():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    # Obtener todos los alumnos ordenados por fecha de registro
    alumnos = Alumno.query.order_by(Alumno.fecha_registro.desc()).all()
    
    # Formatear fechas para el template
    for alumno in alumnos:
        if alumno.fecha_registro:
            alumno.fecha_registro_formatted = alumno.fecha_registro.strftime('%d/%m/%Y')
        else:
            alumno.fecha_registro_formatted = 'N/A'
    
    # Calcular estadísticas
    total_alumnos = len(alumnos)
    alumnos_con_usuario = len([a for a in alumnos if a.usuario_id])
    alumnos_sin_usuario = total_alumnos - alumnos_con_usuario
    ciclos_activos = len(set([a.ciclo for a in alumnos if a.ciclo]))
    
    return render_template('admin/ver_alumnos_moderno.html', 
                         alumnos=alumnos,
                         total_alumnos=total_alumnos,
                         alumnos_con_usuario=alumnos_con_usuario,
                         alumnos_sin_usuario=alumnos_sin_usuario,
                         ciclos_activos=ciclos_activos)

@app.route('/admin/ver_usuarios')
def admin_ver_usuarios():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    # Obtener todos los usuarios ordenados por fecha de creación
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    
    # Formatear fechas para el template
    for usuario in usuarios:
        if usuario.fecha_creacion:
            usuario.fecha_creacion_formatted = usuario.fecha_creacion.strftime('%d/%m/%Y')
        else:
            usuario.fecha_creacion_formatted = 'N/A'
    
    # Calcular estadísticas
    total_usuarios = len(usuarios)
    admin_count = len([u for u in usuarios if u.tipo == 'admin'])
    docente_count = len([u for u in usuarios if u.tipo == 'docente'])
    alumno_count = len([u for u in usuarios if u.tipo == 'alumno'])
    
    return render_template('admin/ver_usuarios_moderno.html', 
                         usuarios=usuarios, 
                         total_usuarios=total_usuarios,
                         admin_count=admin_count,
                         docente_count=docente_count,
                         alumno_count=alumno_count)

@app.route('/admin/ver_materias')
def admin_ver_materias():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    try:
        # Obtener todas las materias con información del docente
        materias_query = db.session.query(Materia, Usuario).outerjoin(Usuario, Materia.docente_id == Usuario.id).order_by(Materia.id.desc()).all()
        
        # Crear una lista con información adicional de notas
        materias = []
        total_notas = 0
        docentes_unicos = set()
        
        for materia, docente in materias_query:
            # Contar las notas para esta materia
            notas_count = Nota.query.filter_by(materia_id=materia.id).count()
            
            materias.append((materia, docente, notas_count))
            total_notas += notas_count
            if docente:
                docentes_unicos.add(docente.id)
        
        # Calcular estadísticas
        total_materias = len(materias)
        docentes_asignados = len(docentes_unicos)
        promedio_notas = round(total_notas / total_materias, 1) if total_materias > 0 else 0
        
        return render_template('admin/ver_materias_moderno.html', 
                             materias=materias,
                             total_materias=total_materias,
                             total_notas=total_notas,
                             docentes_asignados=docentes_asignados,
                             promedio_notas=promedio_notas)
    
    except Exception as e:
        print(f"Error en admin_ver_materias: {e}")
        # En caso de error, devolver una lista vacía
        return render_template('admin/ver_materias_moderno.html', 
                             materias=[],
                             total_materias=0,
                             total_notas=0,
                             docentes_asignados=0,
                             promedio_notas=0)

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
    
    return render_template('admin/registrar_alumno_moderno.html')

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
    
    return render_template('admin/editar_alumno_moderno.html', alumno=alumno)

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
        
        # Manejar eliminación según el tipo de usuario
        if usuario.tipo == 'docente':
            # Si es un docente, eliminar sus materias y notas primero
            materias_docente = Materia.query.filter_by(docente_id=usuario_id).all()
            for materia in materias_docente:
                # Eliminar todas las notas de esta materia
                Nota.query.filter_by(materia_id=materia.id).delete()
            
            # Eliminar las materias del docente
            Materia.query.filter_by(docente_id=usuario_id).delete()
            flash(f'Docente "{usuario.username}" eliminado exitosamente junto con sus materias y notas', 'success')
            
        elif usuario.tipo == 'alumno':
            # Si es un alumno, eliminar sus notas primero
            alumno = Alumno.query.filter_by(usuario_id=usuario_id).first()
            if alumno:
                # Eliminar todas las notas del alumno
                Nota.query.filter_by(alumno_id=alumno.id).delete()
                # Eliminar el registro del alumno
                db.session.delete(alumno)
            flash(f'Alumno "{usuario.username}" eliminado exitosamente junto con sus notas', 'success')
            
        else:
            flash(f'Usuario "{usuario.username}" eliminado exitosamente', 'success')
        
        # Eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        
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
    
    return render_template('admin/editar_usuario_moderno.html', usuario=usuario)

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
            return render_template('admin/crear_materia_moderno.html', docentes=Usuario.query.filter_by(tipo='docente').all())
        
        # Verificar si ya existe una materia con ese código
        materia_existente = Materia.query.filter_by(codigo=codigo).first()
        if materia_existente:
            flash('Ya existe una materia con ese código', 'error')
            return render_template('admin/crear_materia_moderno.html', docentes=Usuario.query.filter_by(tipo='docente').all())
        
        # Verificar que el docente existe
        docente = Usuario.query.filter_by(id=docente_id, tipo='docente').first()
        if not docente:
            flash('El docente seleccionado no es válido', 'error')
            return render_template('admin/crear_materia_moderno.html', docentes=Usuario.query.filter_by(tipo='docente').all())
        
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
    return render_template('admin/crear_materia_moderno.html', docentes=docentes)


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
    
    # Contar las notas del docente
    notas_count = 0
    for materia in materias:
        notas_count += Nota.query.filter_by(materia_id=materia.id).count()
    
    return render_template('docente/dashboard_moderno.html', materias=materias, alumnos=alumnos, notas_count=notas_count)

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
    
    return render_template('docente/agregar_nota_moderno.html', materias=materias, alumnos=alumnos)

@app.route('/docente/ver_notas')
def docente_ver_notas():
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    alumno_id = request.args.get('alumno_id')
    
    # Construir la consulta base
    query = db.session.query(Nota, Alumno, Materia).join(Alumno).join(Materia).filter(Materia.docente_id == docente_id)
    
    # Filtrar por alumno si se especifica
    if alumno_id:
        query = query.filter(Nota.alumno_id == alumno_id)
    
    # Obtener las notas ordenadas por fecha
    notas = query.order_by(Nota.fecha.desc()).all()
    
    # Calcular estadísticas
    total_notas = len(notas)
    notas_aprobadas = len([nota for nota, alumno, materia in notas if nota.nota >= 13])
    notas_recuperacion = len([nota for nota, alumno, materia in notas if 10 <= nota.nota < 13])
    notas_desaprobadas = len([nota for nota, alumno, materia in notas if nota.nota < 10])
    
    # Obtener materias y alumnos para los filtros
    materias = Materia.query.filter_by(docente_id=docente_id).all()
    alumnos = Alumno.query.all()
    
    # Obtener información del alumno seleccionado si existe
    alumno_seleccionado = None
    if alumno_id:
        alumno_seleccionado = Alumno.query.get(alumno_id)
    
    return render_template('docente/ver_notas_moderno.html', 
                         notas=notas,
                         total_notas=total_notas,
                         notas_aprobadas=notas_aprobadas,
                         notas_recuperacion=notas_recuperacion,
                         notas_desaprobadas=notas_desaprobadas,
                         materias=materias,
                         alumnos=alumnos,
                         alumno_seleccionado=alumno_seleccionado,
                         alumno_id_filtro=alumno_id)

@app.route('/docente/editar_nota/<int:nota_id>', methods=['GET', 'POST'])
def editar_nota(nota_id):
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    
    # Obtener la nota y verificar que pertenece a una materia del docente
    nota = db.session.query(Nota, Materia, Alumno).join(Materia).join(Alumno).filter(Nota.id == nota_id, Materia.docente_id == docente_id).first()
    
    if not nota:
        flash('Nota no encontrada o no tienes permisos para editarla', 'error')
        return redirect(url_for('docente_ver_notas'))
    
    nota_obj, materia, alumno = nota
    
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
    
    return render_template('docente/editar_nota_moderno.html', nota=nota_obj, materia=materia, alumno=alumno)

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
    
    # Calcular estadísticas
    total_alumnos = len(alumnos)
    ciclos_unicos = len(set(alumno.ciclo for alumno in alumnos if alumno.ciclo))
    alumnos_con_usuario = len([alumno for alumno in alumnos if alumno.usuario_id])
    
    return render_template('docente/ver_alumnos_moderno.html', 
                         alumnos=alumnos, 
                         total_alumnos=total_alumnos,
                         ciclos_unicos=ciclos_unicos,
                         alumnos_con_usuario=alumnos_con_usuario)

@app.route('/docente/ver_materias')
def docente_ver_materias():
    if not session.get('user_id') or session.get('tipo') != 'docente':
        return redirect(url_for('login'))
    
    docente_id = session['user_id']
    # Obtener todas las materias del docente
    materias = Materia.query.filter_by(docente_id=docente_id).order_by(Materia.id.desc()).all()
    
    # Agregar contador de notas a cada materia
    materias_con_notas = []
    total_notas = 0
    alumnos_unicos = set()
    
    for materia in materias:
        notas_count = Nota.query.filter_by(materia_id=materia.id).count()
        materias_con_notas.append((materia, notas_count))
        total_notas += notas_count
        
        # Contar alumnos únicos que tienen notas en esta materia
        notas_materia = Nota.query.filter_by(materia_id=materia.id).all()
        for nota in notas_materia:
            alumnos_unicos.add(nota.alumno_id)
    
    return render_template('docente/ver_materias_moderno.html', 
                         materias=materias_con_notas,
                         total_notas=total_notas,
                         alumnos_unicos=len(alumnos_unicos))

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
    notas_query = db.session.query(Nota, Alumno).join(Alumno).filter(Nota.materia_id == materia_id).order_by(Nota.fecha.desc()).all()
    
    # Crear una lista con información adicional incluyendo el estado
    notas = []
    for nota, alumno in notas_query:
        # Actualizar notas que no tengan tipo_evaluacion
        if not nota.tipo_evaluacion or nota.tipo_evaluacion.strip() == '':
            nota.tipo_evaluacion = 'Parcial'  # Valor por defecto
            db.session.commit()
        
        # Calcular el estado de la nota
        if nota.nota >= 13:
            estado = "Aprobado"
            clase_estado = "badge-success"  # Verde
        elif nota.nota >= 10:
            estado = "Recuperación"
            clase_estado = "badge-warning"  # Amarillo
        else:
            estado = "Desaprobado"
            clase_estado = "badge-danger"   # Rojo
        
        notas.append((nota, alumno, estado, clase_estado))
    
    return render_template('docente/ver_notas_materia_moderno.html', materia=materia, notas=notas)

# Rutas para el panel del alumno
@app.route('/alumno/dashboard')
def alumno_dashboard():
    if not session.get('user_id') or session.get('tipo') != 'alumno':
        return redirect(url_for('login'))
    
    usuario_id = session['user_id']
    
    # Obtener el alumno asociado al usuario
    alumno = Alumno.query.filter_by(usuario_id=usuario_id).first()
    
    if not alumno:
        flash('No se encontró información del alumno asociada a tu usuario', 'error')
        return redirect(url_for('logout'))
    
    # Obtener todas las notas del alumno con información de materia y docente
    notas_query = db.session.query(Nota, Materia, Usuario).join(Materia, Nota.materia_id == Materia.id).join(Usuario, Materia.docente_id == Usuario.id).filter(Nota.alumno_id == alumno.id).order_by(Nota.fecha.desc()).all()
    
    # Crear una lista con información adicional incluyendo el estado
    notas = []
    for nota, materia, docente in notas_query:
        # Asegurar que tipo_evaluacion no sea None
        if not nota.tipo_evaluacion or nota.tipo_evaluacion.strip() == '':
            nota.tipo_evaluacion = 'Parcial'
            db.session.commit()
        
        # Calcular el estado de la nota
        if nota.nota >= 13:
            estado = "Aprobado"
            clase_estado = "badge-success"  # Verde
        elif nota.nota >= 10:
            estado = "Recuperación"
            clase_estado = "badge-warning"  # Amarillo
        else:
            estado = "Desaprobado"
            clase_estado = "badge-danger"   # Rojo
        
        notas.append((nota, materia, docente, estado, clase_estado))
    
    # Calcular estadísticas
    total_notas = len(notas)
    notas_aprobadas = len([n for n in notas if n[3] == "Aprobado"])
    notas_recuperacion = len([n for n in notas if n[3] == "Recuperación"])
    notas_desaprobadas = len([n for n in notas if n[3] == "Desaprobado"])
    
    # Obtener materias únicas del alumno
    materias_unicas = set()
    for nota, materia, docente, estado, clase_estado in notas:
        materias_unicas.add(materia.id)
    
    total_materias = len(materias_unicas)
    
    # Calcular promedio general basado en el promedio de cada materia
    promedios_materias = []
    materias_aprobadas = 0
    
    for materia_id in materias_unicas:
        notas_materia = [n for n in notas if n[1].id == materia_id]
        if notas_materia:
            promedio_materia = sum([n[0].nota for n in notas_materia]) / len(notas_materia)
            promedios_materias.append(promedio_materia)
            if promedio_materia >= 13:
                materias_aprobadas += 1
    
    # Calcular promedio general como promedio de los promedios de materias
    if promedios_materias:
        promedio_general = sum(promedios_materias) / len(promedios_materias)
    else:
        promedio_general = 0
    
    # Obtener notas recientes (últimas 5)
    notas_recientes = notas[:5] if len(notas) > 5 else notas
    
    return render_template('alumno/dashboard.html', 
                         alumno=alumno, 
                         notas=notas,
                         total_notas=total_notas,
                         notas_aprobadas=notas_aprobadas,
                         notas_recuperacion=notas_recuperacion,
                         notas_desaprobadas=notas_desaprobadas,
                         promedio_general=promedio_general,
                         total_materias=total_materias,
                         materias_aprobadas=materias_aprobadas,
                         notas_recientes=notas_recientes)

@app.route('/alumno/ver_notas')
def alumno_ver_notas():
    if not session.get('user_id') or session.get('tipo') != 'alumno':
        return redirect(url_for('login'))
    
    usuario_id = session['user_id']
    
    # Obtener el alumno asociado al usuario
    alumno = Alumno.query.filter_by(usuario_id=usuario_id).first()
    
    if not alumno:
        flash('No se encontró información del alumno asociada a tu usuario', 'error')
        return redirect(url_for('logout'))
    
    # Obtener todas las notas del alumno con información de materia y docente
    notas_query = db.session.query(Nota, Materia, Usuario).join(Materia, Nota.materia_id == Materia.id).join(Usuario, Materia.docente_id == Usuario.id).filter(Nota.alumno_id == alumno.id).order_by(Nota.fecha.desc()).all()
    
    # Crear una lista con información adicional incluyendo el estado
    notas = []
    for nota, materia, docente in notas_query:
        # Asegurar que tipo_evaluacion no sea None
        if not nota.tipo_evaluacion or nota.tipo_evaluacion.strip() == '':
            nota.tipo_evaluacion = 'Parcial'
            db.session.commit()
        
        # Calcular el estado de la nota
        if nota.nota >= 13:
            estado = "Aprobado"
            clase_estado = "badge-success"  # Verde
        elif nota.nota >= 10:
            estado = "Recuperación"
            clase_estado = "badge-warning"  # Amarillo
        else:
            estado = "Desaprobado"
            clase_estado = "badge-danger"   # Rojo
        
        notas.append((nota, materia, docente, estado, clase_estado))
    
    return render_template('alumno/ver_notas.html', alumno=alumno, notas=notas)

@app.route('/alumno/ver_materias')
def alumno_ver_materias():
    if not session.get('user_id') or session.get('tipo') != 'alumno':
        return redirect(url_for('login'))
    
    usuario_id = session['user_id']
    
    # Obtener el alumno asociado al usuario
    alumno = Alumno.query.filter_by(usuario_id=usuario_id).first()
    
    if not alumno:
        flash('No se encontró información del alumno asociada a tu usuario', 'error')
        return redirect(url_for('logout'))
    
    # Obtener todas las materias donde el alumno tiene notas
    materias_query = db.session.query(Materia, Usuario).join(Usuario, Materia.docente_id == Usuario.id).join(Nota, Nota.materia_id == Materia.id).filter(Nota.alumno_id == alumno.id).distinct().all()
    
    # Crear una lista con información adicional de notas por materia
    materias = []
    for materia, docente in materias_query:
        # Obtener todas las notas del alumno en esta materia
        notas_materia = Nota.query.filter_by(alumno_id=alumno.id, materia_id=materia.id).all()
        
        # Calcular estadísticas de la materia
        total_notas = len(notas_materia)
        if total_notas > 0:
            promedio_materia = sum([n.nota for n in notas_materia]) / total_notas
            ultima_nota = max(notas_materia, key=lambda x: x.fecha)
        else:
            promedio_materia = 0
            ultima_nota = None
        
        materias.append((materia, docente, total_notas, promedio_materia, ultima_nota))
    
    return render_template('alumno/ver_materias.html', alumno=alumno, materias=materias)

@app.route('/alumno/mi_perfil', methods=['GET', 'POST'])
def alumno_mi_perfil():
    if not session.get('user_id') or session.get('tipo') != 'alumno':
        return redirect(url_for('login'))
    
    usuario_id = session['user_id']
    
    # Obtener el alumno asociado al usuario
    alumno = Alumno.query.filter_by(usuario_id=usuario_id).first()
    
    if not alumno:
        flash('No se encontró información del alumno asociada a tu usuario', 'error')
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        try:
            # Solo actualizar campos editables por el alumno
            alumno.email = request.form.get('email')
            alumno.telefono = request.form.get('telefono')
            
            # Actualizar información del usuario
            usuario = Usuario.query.get(usuario_id)
            if usuario:
                usuario.email = request.form.get('email')
                nueva_password = request.form.get('password')
                if nueva_password and nueva_password.strip():
                    usuario.password_hash = generate_password_hash(nueva_password)
            
                db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('alumno_mi_perfil'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el perfil. Inténtalo de nuevo.', 'error')
            print(f"Error al actualizar perfil: {e}")
    
    return render_template('alumno/mi_perfil.html', alumno=alumno)

@app.route('/admin/mi_perfil', methods=['GET', 'POST'])
def admin_mi_perfil():
    if not session.get('user_id') or session.get('tipo') != 'admin':
        return redirect(url_for('login'))
    
    usuario_id = session['user_id']
    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        flash('No se encontró información del usuario', 'error')
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        try:
            # Actualizar información del usuario
            usuario.username = request.form['username']
            usuario.email = request.form['email']
            
            nueva_password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if nueva_password and nueva_password.strip():
                if nueva_password != confirm_password:
                    flash('Las contraseñas no coinciden', 'error')
                    return redirect(url_for('admin_mi_perfil'))
                usuario.password_hash = generate_password_hash(nueva_password)
            
        db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('admin_mi_perfil'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el perfil. Inténtalo de nuevo.', 'error')
            print(f"Error al actualizar perfil: {e}")
    
    return render_template('admin/mi_perfil.html', usuario=usuario)

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
            
            # Calcular el estado de la nota
            if nota.nota >= 13:
                estado = "Aprobado"
                clase_estado = "badge-success"  # Verde
            elif nota.nota >= 10:
                estado = "Recuperación"
                clase_estado = "badge-warning"  # Amarillo
            else:
                estado = "Desaprobado"
                clase_estado = "badge-danger"   # Rojo
            
            notas.append((nota, materia, docente, estado, clase_estado))
        
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
