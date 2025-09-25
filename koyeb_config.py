#!/usr/bin/env python3
"""
Configuración específica para Koyeb
Este archivo maneja la configuración de la aplicación para el despliegue en Koyeb
"""

import os
from app import app, db

def init_koyeb():
    """Inicializar la aplicación para Koyeb"""
    print("🚀 Inicializando aplicación para Koyeb...")
    
    # Crear tablas si no existen
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
            return False
    
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
        return False
    
    print("✅ Aplicación inicializada correctamente para Koyeb")
    return True

if __name__ == '__main__':
    init_koyeb()
