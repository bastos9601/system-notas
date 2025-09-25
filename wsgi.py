#!/usr/bin/env python3
"""
Archivo WSGI para Koyeb
Este archivo es el punto de entrada para la aplicación en producción
"""

import os
from app import app, db

def init_app():
    """Inicializar la aplicación"""
    print("🚀 Inicializando aplicación...")
    
    # Crear tablas si no existen
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada")
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
            raise e
    
    # Crear usuario administrador si no existe
    try:
        from app import Usuario
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
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {e}")
        # No lanzar excepción aquí para no bloquear el inicio

# Inicializar la aplicación
init_app()

# Exportar la aplicación para WSGI
application = app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
