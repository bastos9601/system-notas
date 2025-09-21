@echo off
echo ========================================
echo    SISTEMA DE NOTAS - INSTALACION
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.7 o superior desde: https://python.org
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo    INSTALACION COMPLETADA
echo ========================================
echo.
echo Para iniciar el sistema:
echo 1. Ejecuta: python run.py
echo 2. O ejecuta: python app.py
echo.
echo El sistema estara disponible en:
echo - Local: http://localhost:5000
echo - Red: http://[tu-ip]:5000
echo.
echo Usuario administrador:
echo - Usuario: admin
echo - Contraseña: admin123
echo.
echo ========================================
pause
