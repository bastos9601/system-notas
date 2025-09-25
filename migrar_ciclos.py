#!/usr/bin/env python3
"""
Script para migrar ciclos de números a texto
Este script convierte los ciclos existentes en la base de datos de números a texto
"""

import os
import sys
from app import app, db, Alumno, convertir_ciclo_a_texto

def migrar_ciclos():
    """Migrar todos los ciclos de números a texto"""
    print("🔄 Iniciando migración de ciclos...")
    
    with app.app_context():
        try:
            # Obtener todos los alumnos
            alumnos = Alumno.query.all()
            print(f"📊 Encontrados {len(alumnos)} alumnos para migrar")
            
            migrados = 0
            sin_cambios = 0
            
            for alumno in alumnos:
                ciclo_original = alumno.ciclo
                ciclo_nuevo = convertir_ciclo_a_texto(ciclo_original)
                
                if ciclo_original != ciclo_nuevo:
                    print(f"🔄 Migrando: {alumno.nombre} {alumno.apellido} - {ciclo_original} → {ciclo_nuevo}")
                    alumno.ciclo = ciclo_nuevo
                    migrados += 1
                else:
                    sin_cambios += 1
            
            # Guardar cambios
            if migrados > 0:
                db.session.commit()
                print(f"✅ Migración completada:")
                print(f"   - {migrados} alumnos migrados")
                print(f"   - {sin_cambios} alumnos sin cambios")
            else:
                print(f"ℹ️  No se encontraron ciclos para migrar")
                print(f"   - {sin_cambios} alumnos ya tienen formato correcto")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante la migración: {e}")
            return False
    
    return True

def verificar_ciclos():
    """Verificar el estado actual de los ciclos"""
    print("🔍 Verificando estado actual de los ciclos...")
    
    with app.app_context():
        try:
            alumnos = Alumno.query.all()
            ciclos_unicos = set()
            
            for alumno in alumnos:
                if alumno.ciclo:
                    ciclos_unicos.add(alumno.ciclo)
            
            print(f"📊 Ciclos encontrados en la base de datos:")
            for ciclo in sorted(ciclos_unicos):
                count = Alumno.query.filter_by(ciclo=ciclo).count()
                print(f"   - '{ciclo}': {count} alumnos")
                
        except Exception as e:
            print(f"❌ Error al verificar ciclos: {e}")

def main():
    """Función principal"""
    print("🚀 Migración de Ciclos - Sistema de Notas")
    print("=" * 50)
    
    # Verificar estado actual
    verificar_ciclos()
    print()
    
    # Preguntar si continuar
    respuesta = input("¿Deseas continuar con la migración? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        if migrar_ciclos():
            print()
            print("🔍 Verificando resultado...")
            verificar_ciclos()
            print()
            print("✅ Migración completada exitosamente")
        else:
            print("❌ La migración falló")
    else:
        print("❌ Migración cancelada por el usuario")

if __name__ == '__main__':
    main()
