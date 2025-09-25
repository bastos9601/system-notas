#!/usr/bin/env python3
"""
Script de depuración para Koyeb
Este script ayuda a diagnosticar problemas en el despliegue
"""

import os
import sys

def check_environment():
    """Verificar el entorno de Koyeb"""
    print("🔍 Verificando entorno de Koyeb...")
    print("=" * 50)
    
    # Verificar variables de entorno
    env_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'FLASK_ENV',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if var == 'SECRET_KEY':
                print(f"✅ {var}: {'*' * 20} (configurado)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: No configurado")
    
    print("=" * 50)

def test_database_connection():
    """Probar la conexión a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        from app import app, db
        
        with app.app_context():
            # Probar una consulta simple
            from app import Usuario
            count = Usuario.query.count()
            print(f"✅ Conexión a base de datos exitosa. Usuarios: {count}")
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False

def test_imports():
    """Probar que todas las importaciones funcionen"""
    print("🔍 Probando importaciones...")
    
    try:
        from app import app, db, Usuario, Alumno, Materia, Nota
        print("✅ Todas las importaciones exitosas")
        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_templates():
    """Verificar que las plantillas existan"""
    print("🔍 Verificando plantillas...")
    
    required_templates = [
        'admin/dashboard_moderno.html',
        'login_moderno.html',
        'error.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        template_path = f"templates/{template}"
        if os.path.exists(template_path):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - FALTANTE")
            missing_templates.append(template)
    
    return len(missing_templates) == 0

def main():
    """Función principal de diagnóstico"""
    print("🚀 Diagnóstico de Koyeb - Sistema de Notas")
    print("=" * 60)
    
    # Verificar entorno
    check_environment()
    
    # Probar importaciones
    if not test_imports():
        print("❌ Error crítico: No se pueden importar los módulos")
        sys.exit(1)
    
    # Probar plantillas
    if not test_templates():
        print("❌ Error crítico: Faltan plantillas importantes")
        sys.exit(1)
    
    # Probar base de datos
    if not test_database_connection():
        print("❌ Error crítico: No se puede conectar a la base de datos")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ Diagnóstico completado - Todo parece estar funcionando")
    print("📋 Si sigues teniendo problemas:")
    print("   1. Revisa los logs de Koyeb para errores específicos")
    print("   2. Verifica que las variables de entorno estén configuradas")
    print("   3. Asegúrate de tener una base de datos PostgreSQL")
    print("=" * 60)

if __name__ == '__main__':
    main()
