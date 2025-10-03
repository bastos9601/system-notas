#!/usr/bin/env python3
"""
Script de inicio para el Sistema de Notas
Ejecuta la aplicación Flask con configuración optimizada
"""

import os
import sys
from app import app, db

def create_tables():
    """Crear tablas de la base de datos si no existen"""
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada correctamente")

def create_admin_user():
    """Crear usuario administrador por defecto si no existe"""
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
            print("✅ Usuario administrador creado:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   ⚠️  IMPORTANTE: Cambia la contraseña después del primer inicio")
        else:
            print("✅ Usuario administrador ya existe")

def main():
    """Función principal"""
    print("🚀 Iniciando Sistema de Notas...")
    print("=" * 50)
    
    # Crear tablas
    create_tables()
    
    # Crear usuario admin
    create_admin_user()
    
    print("=" * 50)
    print("🌐 Servidor iniciado en:")
    print("   Local: http://localhost:5000")
    print("   Red: http://0.0.0.0:5000")
    print("=" * 50)
    print("📱 Para acceder desde móviles/tablets:")
    print("   1. Conecta el dispositivo a la misma red WiFi")
    print("   2. Ve a: http://[IP-DE-TU-PC]:5000")
    print("   3. Para encontrar tu IP, ejecuta: ipconfig (Windows) o ifconfig (Mac/Linux)")
    print("=" * 50)
    print("👤 Usuario administrador:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("=" * 50)
    print("🛑 Para detener el servidor: Ctrl+C")
    print("=" * 50)
    
    # Iniciar servidor
    try:
        app.run(
            debug=True,
            host='0.0.0.0',  # Permite acceso desde otros dispositivos
            port=5000,
            threaded=True,   # Mejor rendimiento
            use_reloader=True,  # Auto-reload cuando cambien los archivos
            use_debugger=True   # Debugger integrado
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
