#!/usr/bin/env python3
"""
Script de configuración para Koyeb
Ejecuta este script antes del despliegue para verificar la configuración
"""

import os
import sys

def check_requirements():
    """Verificar que todos los archivos necesarios estén presentes"""
    required_files = [
        'app.py',
        'requirements.txt',
        'Procfile',
        'wsgi.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos los archivos requeridos están presentes")
    return True

def check_environment():
    """Verificar variables de entorno"""
    print("🔍 Verificando configuración de entorno...")
    
    # Verificar SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key or secret_key == 'tu_clave_secreta_aqui_cambiar_en_produccion':
        print("⚠️  SECRET_KEY no está configurado o usa el valor por defecto")
        print("   Configura una SECRET_KEY segura en Koyeb")
    else:
        print("✅ SECRET_KEY configurado")
    
    # Verificar DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️  DATABASE_URL no está configurado")
        print("   Asegúrate de tener una base de datos PostgreSQL configurada en Koyeb")
    else:
        print("✅ DATABASE_URL configurado")
        if database_url.startswith('postgres://'):
            print("   ⚠️  URL de PostgreSQL detectada, se convertirá automáticamente")
    
    return True

def main():
    """Función principal"""
    print("🚀 Verificando configuración para Koyeb...")
    print("=" * 50)
    
    # Verificar archivos
    if not check_requirements():
        sys.exit(1)
    
    # Verificar entorno
    check_environment()
    
    print("=" * 50)
    print("✅ Configuración verificada")
    print("📋 Pasos para el despliegue en Koyeb:")
    print("   1. Conecta tu repositorio a Koyeb")
    print("   2. Configura las variables de entorno:")
    print("      - SECRET_KEY: Una clave secreta segura")
    print("   3. Añade una base de datos PostgreSQL")
    print("   4. Despliega la aplicación")
    print("=" * 50)

if __name__ == '__main__':
    main()
