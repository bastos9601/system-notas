#!/bin/bash

echo "========================================"
echo "   SISTEMA DE NOTAS - INSTALACION"
echo "========================================"
echo

# Verificar Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Por favor instala Python 3.7 o superior"
    exit 1
fi

echo "Python encontrado!"
echo

# Verificar pip
echo "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 no está instalado"
    echo "Por favor instala pip3"
    exit 1
fi

echo "pip encontrado!"
echo

# Instalar dependencias
echo "Instalando dependencias..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias"
    exit 1
fi

echo
echo "========================================"
echo "   INSTALACION COMPLETADA"
echo "========================================"
echo
echo "Para iniciar el sistema:"
echo "1. Ejecuta: python3 run.py"
echo "2. O ejecuta: python3 app.py"
echo
echo "El sistema estará disponible en:"
echo "- Local: http://localhost:5000"
echo "- Red: http://[tu-ip]:5000"
echo
echo "Usuario administrador:"
echo "- Usuario: admin"
echo "- Contraseña: admin123"
echo
echo "========================================"
