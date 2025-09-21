# Sistema de Notas

Un sistema web para la gestión de notas académicas desarrollado con Flask.

## Características

- **Gestión de usuarios**: Administradores y docentes
- **Registro de alumnos**: Con información completa
- **Gestión de materias**: Por docente
- **Sistema de notas**: Evaluaciones y calificaciones
- **Consulta pública**: Los alumnos pueden consultar sus notas con DNI

## Despliegue en Koyeb

### 1. Preparación del proyecto

El proyecto ya está configurado para desplegarse en Koyeb. Los archivos necesarios son:

- `Procfile`: Define cómo ejecutar la aplicación con gunicorn
- `requirements.txt`: Dependencias de Python
- `runtime.txt`: Versión de Python
- `app.py`: Aplicación principal con configuración de producción

### 2. Crear cuenta en Koyeb

1. Ve a [koyeb.com](https://koyeb.com)
2. Crea una cuenta gratuita
3. Verifica tu email

### 3. Conectar repositorio

1. En el dashboard de Koyeb, haz clic en "Create Service"
2. Selecciona "GitHub" como fuente
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio de tu proyecto

### 4. Configurar base de datos PostgreSQL

**IMPORTANTE**: Tu proyecto ya está configurado para usar PostgreSQL en producción.

1. En Koyeb, ve a "Databases"
2. Crea una nueva base de datos PostgreSQL
3. Copia la URL de conexión (formato: `postgres://usuario:password@host:puerto/database`)
4. **NO** cambies el formato de la URL, el código la convierte automáticamente

### 5. Configurar variables de entorno

En la sección "Environment Variables" de Koyeb, agrega:

```
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
DATABASE_URL=postgres://usuario:password@host:puerto/database
FLASK_ENV=production
```

**⚠️ IMPORTANTE**: 
- Cambia `SECRET_KEY` por una clave segura y única
- Usa la URL exacta que te da Koyeb para PostgreSQL
- El código convierte automáticamente `postgres://` a `postgresql://`

### 6. Desplegar

1. Haz clic en "Guardar e implementar" → "Con construcción"
2. Koyeb construirá y desplegará tu aplicación automáticamente
3. Una vez completado, tendrás una URL pública
4. **La base de datos se creará automáticamente** con las tablas necesarias

## Uso local

### Instalación

1. Clona el repositorio
2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Configuración

1. Copia `env.example` a `.env`
2. Edita `.env` con tus configuraciones
3. Ejecuta la aplicación:
   ```bash
   python run.py
   ```

### Acceso

- **URL local**: http://localhost:5000
- **Usuario admin**: admin
- **Contraseña**: admin123

**⚠️ IMPORTANTE**: Cambia la contraseña del administrador después del primer inicio.

## Estructura del proyecto

```
sistemas-notas/
├── app.py              # Aplicación principal
├── run.py              # Script de inicio para desarrollo
├── requirements.txt    # Dependencias
├── Procfile           # Configuración para Koyeb (gunicorn)
├── runtime.txt        # Versión de Python
├── .gitignore         # Archivos a ignorar
├── env.example        # Variables de entorno de ejemplo
├── templates/         # Plantillas HTML
├── static/           # Archivos estáticos (CSS, JS)
└── instance/         # Base de datos local
```

## Funcionalidades

### Para Administradores
- Crear y gestionar usuarios (admin/docente)
- Registrar alumnos
- Ver todas las notas del sistema
- Editar información de alumnos

### Para Docentes
- Crear materias
- Agregar notas a alumnos
- Ver notas de sus materias
- Editar y eliminar notas

### Para Alumnos (consulta pública)
- Consultar notas ingresando DNI
- Ver historial completo de calificaciones

## Tecnologías utilizadas

- **Backend**: Flask (Python)
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML, CSS, JavaScript
- **Servidor WSGI**: Gunicorn
- **Despliegue**: Koyeb

## Solución de problemas

### Error "TCP health check failed on port 8000"
Este error se solucionó usando gunicorn en lugar del servidor de desarrollo de Flask.

### Variables de entorno importantes
- `SECRET_KEY`: Clave secreta para Flask (obligatoria en producción)
- `DATABASE_URL`: URL de conexión a la base de datos
- `FLASK_ENV`: Entorno (development/production)
- `PORT`: Puerto (Koyeb lo configura automáticamente)

## Soporte

Si tienes problemas con el despliegue o el uso del sistema, revisa:

1. Los logs de Koyeb en el dashboard
2. Las variables de entorno están configuradas correctamente
3. La base de datos está conectada
4. El archivo `Procfile` está presente y usa gunicorn

## Licencia

Este proyecto es de uso educativo.
