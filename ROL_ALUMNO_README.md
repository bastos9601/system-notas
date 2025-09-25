# 🎓 Nuevo Rol de Alumno - Sistema de Notas

## 📋 Descripción

Se ha agregado un nuevo rol **"alumno"** al sistema de notas, permitiendo que los alumnos tengan su propio panel de acceso para consultar sus notas y materias.

## ✨ Nuevas Funcionalidades

### 🔐 Autenticación de Alumnos
- Los alumnos ahora pueden iniciar sesión con sus propias credenciales
- Panel de alumno personalizado con información relevante
- Acceso restringido solo a sus propias notas y materias

### 📊 Panel del Alumno
- **Dashboard principal** con estadísticas personales
- **Ver todas las notas** con estado (Aprobado/Recuperación/Desaprobado)
- **Ver materias** con promedios y estadísticas por materia
- **Información personal** del alumno

### 👨‍💼 Panel de Administración
- **Crear usuarios para alumnos** desde el panel de administración
- **Asociar usuarios con alumnos** existentes
- **Gestión completa** de usuarios de tipo alumno

## 🚀 Instalación y Configuración

### 1. Inicializar la Base de Datos
```bash
python init_alumno_role.py
```

### 2. Ejecutar la Aplicación
```bash
python app.py
```

### 3. Acceder como Administrador
- URL: `http://localhost:5000/login`
- Usuario: `admin`
- Contraseña: `admin123`

## 📝 Cómo Usar el Nuevo Rol

### Para Administradores

#### 1. Crear Usuario para Alumno
1. Ir al **Panel de Administración**
2. Hacer clic en **"Crear Usuario para Alumno"**
3. Seleccionar un alumno de la lista (solo aparecen alumnos sin usuario)
4. Ingresar:
   - Nombre de usuario
   - Email
   - Contraseña
5. Hacer clic en **"Crear Usuario"**

#### 2. Crear Usuario General (incluye opción de alumno)
1. Ir al **Panel de Administración**
2. Hacer clic en **"Crear Usuario"**
3. Seleccionar tipo **"Alumno"**
4. Seleccionar el alumno correspondiente
5. Completar los datos del usuario

### Para Alumnos

#### 1. Acceder al Sistema
1. Ir a `http://localhost:5000/login`
2. Ingresar las credenciales proporcionadas por el administrador
3. Será redirigido automáticamente al **Panel del Alumno**

#### 2. Navegar en el Panel
- **Dashboard**: Ver estadísticas generales y últimas notas
- **Mis Notas**: Ver todas las notas con detalles completos
- **Mis Materias**: Ver materias con promedios y estadísticas

## 🗂️ Estructura de Archivos Agregados

```
templates/
├── alumno/
│   ├── dashboard.html          # Panel principal del alumno
│   ├── ver_notas.html          # Ver todas las notas
│   └── ver_materias.html       # Ver materias con estadísticas
└── admin/
    └── crear_usuario_alumno.html  # Formulario específico para crear usuarios de alumnos

init_alumno_role.py              # Script de inicialización
ROL_ALUMNO_README.md            # Este archivo de documentación
```

## 🔧 Cambios Técnicos Realizados

### Base de Datos
- **Tabla Usuario**: Campo `tipo` ahora acepta 'alumno'
- **Tabla Alumno**: Agregada columna `usuario_id` para relación con Usuario
- **Relación**: Usuario ↔ Alumno (uno a uno)

### Rutas Agregadas
- `/alumno/dashboard` - Panel principal del alumno
- `/alumno/ver_notas` - Ver todas las notas del alumno
- `/alumno/ver_materias` - Ver materias del alumno
- `/admin/crear_usuario_alumno` - Crear usuario específico para alumno

### Autenticación
- Sistema de login actualizado para redirigir alumnos al panel correspondiente
- Verificación de permisos en todas las rutas del alumno
- Asociación automática entre usuario y alumno

## 🎯 Características del Panel del Alumno

### Dashboard Principal
- **Estadísticas personales**: Total de notas, aprobadas, en recuperación, desaprobadas
- **Promedio general** de todas las notas
- **Últimas notas** registradas
- **Información personal** del alumno

### Vista de Notas
- **Tabla completa** de todas las notas
- **Estado visual** con colores (Verde=Aprobado, Amarillo=Recuperación, Rojo=Desaprobado)
- **Información detallada**: Materia, docente, tipo de evaluación, fecha, observaciones
- **Resumen por materia** con promedios

### Vista de Materias
- **Tarjetas por materia** con información completa
- **Estadísticas por materia**: Total de notas, promedio, última nota
- **Información del docente** de cada materia
- **Estado general** de cada materia

## 🔒 Seguridad

- **Acceso restringido**: Los alumnos solo pueden ver sus propias notas
- **Verificación de permisos**: Todas las rutas verifican el tipo de usuario
- **Asociación segura**: Solo se pueden crear usuarios para alumnos existentes
- **Validación de datos**: Verificación de que el alumno no tenga ya un usuario

## 🐛 Solución de Problemas

### Error: "No se encontró información del alumno"
- **Causa**: El usuario de tipo alumno no está asociado con un registro de Alumno
- **Solución**: Verificar que el usuario tenga un `usuario_id` válido en la tabla Alumno

### Error: "El alumno ya tiene un usuario asociado"
- **Causa**: Se intenta crear un usuario para un alumno que ya tiene uno
- **Solución**: Verificar en la base de datos o usar un alumno diferente

### No aparecen alumnos en la lista de selección
- **Causa**: Todos los alumnos ya tienen usuarios asociados
- **Solución**: Registrar nuevos alumnos o verificar la base de datos

## 📞 Soporte

Si encuentras algún problema o tienes preguntas sobre el nuevo rol de alumno, revisa:

1. **Logs de la aplicación** para errores específicos
2. **Base de datos** para verificar las relaciones
3. **Este archivo** para instrucciones detalladas

---

**¡El nuevo rol de alumno está listo para usar! 🎉**
