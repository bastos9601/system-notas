#!/usr/bin/env python3
"""
Script de desarrollo para el Sistema de Notas
Inicia la aplicación con auto-reload habilitado
"""

import os
import sys
from app import app, db

def main():
    """Función principal para desarrollo"""
    print("🚀 Iniciando Sistema de Notas en modo DESARROLLO...")
    print("=" * 60)
    print("🔄 AUTO-RELOAD HABILITADO - Los cambios se aplicarán automáticamente")
    print("=" * 60)
    
    # Configurar variables de entorno para desarrollo
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🌐 Servidor iniciado en:")
    print("   Local: http://localhost:5000")
    print("   Red: http://0.0.0.0:5000")
    print("=" * 60)
    print("👤 Usuario administrador:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("=" * 60)
    print("🛑 Para detener el servidor: Ctrl+C")
    print("=" * 60)
    
    # Iniciar servidor con auto-reload
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True,
            use_reloader=True,    # Auto-reload cuando cambien los archivos
            use_debugger=True,    # Debugger integrado
            reloader_type='stat'  # Tipo de reloader más rápido
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
