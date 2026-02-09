# Sistema de Autenticación y Control de Acceso

## Credenciales por Defecto

La aplicación viene configurada con un usuario de administrador por defecto:

- **Usuario:** `admin`
- **Contraseña:** `admin123`

## Roles y Permisos

### 1. ADMIN
- Acceso completo a todas las funciones
- Crear, editar y eliminar usuarios
- Cambiar roles de otros usuarios
- Registrar entregas y recepciones
- Registrar incidencias
- Ver histórico y borrar registros
- Acceso a panel de administración

### 2. OPERATOR
- Registrar entregas y recepciones
- Registrar incidencias
- Ver histórico completo
- Borrar registros (entregas, recepciones, incidencias)
- Ver lista de incidencias
- Exportar datos
- **No puede:** Crear usuarios ni modificar roles

### 3. VIEWER
- Ver histórico de entregas y recepciones (solo lectura)
- Ver lista de incidencias (solo lectura)
- Exportar datos en Excel
- **No puede:** Registrar, borrar, modificar datos, ni crear usuarios

## Flujo de Uso

### Primer Acceso (Administrador)
1. Acceder a `http://localhost:5000`
2. Login con `admin` / `admin123`
3. Ir a "Administración" (botón en la esquina superior)
4. Cambiar la contraseña del admin (recomendado)
5. Crear otros usuarios según sea necesario

### Crear Nuevo Usuario
1. Iniciar sesión como admin
2. Ir a "Administración"
3. Hacer clic en "+ Crear Usuario"
4. Completar:
   - Nombre de usuario
   - Contraseña (mínimo 6 caracteres)
   - Rol (Admin, Operator o Viewer)
5. Hacer clic en "Crear Usuario"

### Editar Usuario Existente
1. Ir a "Administración"
2. Hacer clic en "Editar" al lado del usuario
3. Cambiar el rol o desactivar el usuario
4. Hacer clic en "Guardar Cambios"

### Eliminar Usuario
1. Ir a "Administración"
2. Hacer clic en "Eliminar" al lado del usuario
3. Confirmar la eliminación

## Cambiar Contraseña

Por el momento, el sistema solo permite cambiar contraseña a través del admin editando el usuario. Para un cambio de contraseña propio:
1. Contactar al administrador para que edite la cuenta
2. O usar el script `reset_password.py` si tienes acceso al servidor

## Recomendaciones de Seguridad

1. **Cambia la contraseña del admin** inmediatamente después de la instalación
2. **Usa contraseñas fuertes** para todos los usuarios
3. **Revisa regularmente** la lista de usuarios activos en administración
4. **Desactiva usuarios** en lugar de eliminarlos si necesitas conservar histórico
5. **Limita el acceso admin** solo a personal de confianza

## Tabla de Permisos Detallada

| Permiso | Admin | Operator | Viewer |
|---------|-------|----------|--------|
| Registrar entrega | ✓ | ✓ | ✗ |
| Registrar recepción | ✓ | ✓ | ✗ |
| Registrar incidencia | ✓ | ✓ | ✗ |
| Ver histórico | ✓ | ✓ | ✓ |
| Ver incidencias | ✓ | ✓ | ✓ |
| Borrar registros | ✓ | ✓ | ✗ |
| Exportar Excel | ✓ | ✓ | ✓ |
| Importar datos | ✓ | ✓ | ✗ |
| Crear usuarios | ✓ | ✗ | ✗ |
| Editar roles | ✓ | ✗ | ✗ |
| Eliminar usuarios | ✓ | ✗ | ✗ |
| Panel administración | ✓ | ✗ | ✗ |

## Troubleshooting

### Olvidé la contraseña
1. Accede a la base de datos `entregas.db`
2. O ejecuta el script `reset_admin_password.py` en el servidor
3. Se asignará la contraseña por defecto `admin123`

### Usuario no puede acceder
1. Verifica que la cuenta esté **Activa** en el panel de administración
2. Verifica que el usuario tenga la contraseña correcta
3. Intenta resetear la contraseña del usuario

### Permiso denegado en una función
1. Verifica el rol del usuario en administración
2. Consulta la tabla de permisos arriba
3. Cambia el rol si es necesario
