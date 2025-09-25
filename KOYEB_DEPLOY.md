# 🚀 Despliegue en Koyeb - Sistema de Notas

## 📋 Pasos para Desplegar

### 1. Preparar el Repositorio
- ✅ Todos los archivos están listos
- ✅ `requirements.txt` configurado
- ✅ `Procfile` configurado
- ✅ `wsgi.py` creado para producción

### 2. Configurar en Koyeb

#### Variables de Entorno Requeridas:
```
SECRET_KEY=tu_clave_secreta_muy_segura_para_produccion
FLASK_ENV=production
FLASK_DEBUG=False
```

#### Base de Datos:
- Añade una base de datos PostgreSQL en Koyeb
- La `DATABASE_URL` se configurará automáticamente

### 3. Posibles Problemas y Soluciones

#### Error 500 - Internal Server Error

**Causas Comunes:**
1. **Base de datos no configurada**
   - Solución: Añade una base de datos PostgreSQL en Koyeb

2. **SECRET_KEY no configurado**
   - Solución: Configura una SECRET_KEY segura en las variables de entorno

3. **Dependencias faltantes**
   - Solución: Verifica que `requirements.txt` esté completo

4. **Error en la inicialización de la base de datos**
   - Solución: Revisa los logs de Koyeb para ver el error específico

#### Verificar Logs en Koyeb:
1. Ve al panel de Koyeb
2. Selecciona tu aplicación
3. Ve a la pestaña "Logs"
4. Busca errores específicos

### 4. Archivos de Configuración

- `wsgi.py` - Punto de entrada para producción
- `Procfile` - Configuración de Gunicorn
- `requirements.txt` - Dependencias de Python
- `koyeb_setup.py` - Script de verificación

### 5. Comandos de Verificación

```bash
# Verificar configuración localmente
python koyeb_setup.py

# Probar la aplicación localmente
python wsgi.py
```

### 6. Solución de Problemas

Si sigues teniendo errores:

1. **Revisa los logs de Koyeb** para el error específico
2. **Verifica las variables de entorno** en el panel de Koyeb
3. **Asegúrate de tener una base de datos PostgreSQL** configurada
4. **Verifica que el repositorio esté actualizado** con todos los archivos

### 7. Contacto

Si necesitas ayuda adicional, proporciona:
- Los logs de error de Koyeb
- Las variables de entorno configuradas
- El estado de la base de datos
