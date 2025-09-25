#!/usr/bin/env python3
"""
Archivo WSGI para Koyeb
Este archivo es el punto de entrada para la aplicación en producción
"""

import os
import sys

def init_app():
    """Inicializar la aplicación de forma segura"""
    print("🚀 Inicializando aplicación...")
    
    try:
        from app import app, db
        from error_handler import init_database_safely, create_admin_user_safely
        
        # Inicializar base de datos de forma segura
        if not init_database_safely():
            print("⚠️  Base de datos no se pudo inicializar completamente")
        
        # Crear usuario administrador de forma segura
        if not create_admin_user_safely():
            print("⚠️  Usuario administrador no se pudo crear completamente")
        
        print("✅ Aplicación inicializada correctamente")
        return app
        
    except Exception as e:
        print(f"❌ Error crítico al inicializar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Inicializar la aplicación
application = init_app()

if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
