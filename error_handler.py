#!/usr/bin/env python3
"""
Manejador de errores para producción
Este archivo proporciona funciones para manejar errores de forma robusta
"""

import traceback
import sys

def log_error(error, context=""):
    """Registrar errores de forma segura"""
    try:
        error_msg = f"Error en {context}: {str(error)}"
        print(error_msg)
        
        # En producción, también podrías enviar esto a un servicio de logging
        # como Sentry, Loggly, etc.
        
    except Exception as e:
        print(f"Error al registrar error: {e}")

def safe_query(query_func, default_value=None, context=""):
    """Ejecutar consultas de base de datos de forma segura"""
    try:
        return query_func()
    except Exception as e:
        log_error(e, f"Query error in {context}")
        return default_value if default_value is not None else []

def safe_render_template(template_name, **kwargs):
    """Renderizar plantillas de forma segura"""
    try:
        from flask import render_template
        return render_template(template_name, **kwargs)
    except Exception as e:
        log_error(e, f"Template rendering error for {template_name}")
        # Renderizar una plantilla de error simple
        try:
            return render_template('error.html', error=str(e))
        except:
            return f"<h1>Error</h1><p>Error al cargar la página: {str(e)}</p>"

def init_database_safely():
    """Inicializar la base de datos de forma segura"""
    try:
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            return True
    except Exception as e:
        log_error(e, "Database initialization")
        return False

def create_admin_user_safely():
    """Crear usuario administrador de forma segura"""
    try:
        from app import app, db, Usuario
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
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
                print("✅ Usuario administrador creado")
            else:
                print("✅ Usuario administrador ya existe")
            return True
    except Exception as e:
        log_error(e, "Admin user creation")
        return False
