# 📁 Estructura del Proyecto Actualizado

```
APP-IT-PMR/
│
├── 📄 app.py                          # Aplicación principal (ACTUALIZADO - Añadido auth)
├── 📄 requirements.txt                # Dependencias (ACTUALIZADO - Añadido Flask-Login)
├── 📄 README.md                       # README original
│
├── 🔐 AUTENTICACION.md               # Documentación de autenticación (NUEVO)
├── 🚀 INICIO_RAPIDO.md               # Guía de inicio rápido (NUEVO)  
├── 📋 RESUMEN_IMPLEMENTACION.md      # Resumen técnico de cambios (NUEVO)
│
├── 📦 templates/                      # Plantillas HTML
│   ├── index.html                     # Página principal (ACTUALIZADO)
│   ├── history.html                   # Histórico de registros (ACTUALIZADO)
│   ├── incidents.html                 # Gestión de incidencias (ACTUALIZADO)
│   ├── import.html                    # Importar datos (ACTUALIZADO)
│   ├── import_result.html             # Resultado de importación (ACTUALIZADO)
│   │
│   ├── 🆕 login.html                  # Página de login (NUEVO)
│   ├── 🆕 administracion.html         # Panel administrativo (NUEVO)
│   ├── 🆕 crear_usuario.html          # Crear usuario nuevo (NUEVO)
│   └── 🆕 editar_usuario.html         # Editar usuario existente (NUEVO)
│
├── 🎨 static/                         # Archivos estáticos
│   ├── app.js                         # JavaScript del cliente
│   └── style.css                      # Estilos CSS
│
├── 📊 pdfs/                           # Directorio de PDFs
│   └── entregas/                      # PDFs de entregas
│
├── 📁 scripts/                        # Scripts auxiliares
│   ├── import_sample.py               # Script de importación
│   └── print_db.py                    # Script de debugging
│
├── 🗄️ entregas.db                    # Base de datos SQLite (actualizada con tabla usuarios)
│
├── 📦 sample_import.csv               # Archivo de ejemplo para importar
│
├── 🚀 start.bat                       # Script para iniciar en Windows
├── 🚀 start.ps1                       # Script PowerShell para iniciar
├── 🚀 start_with_browser.bat          # Inicia y abre navegador
├── 🔧 install.bat                     # Script de instalación
│
└── 📄 .gitignore                      # Archivos ignorados por git
```

## 🆕 Cambios Realizados

### Modificaciones en `app.py`:

```python
# NUEVO: Importaciones de autenticación
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# NUEVO: Configuración de saltos secret
app.secret_key = 'your-secret-key-change-this-in-production'

# NUEVO: Tabla de usuarios
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL,
    activo INTEGER DEFAULT 1,
    fecha_creacion TEXT
)

# NUEVO: Estructura de roles y permisos
ROLES_PERMISOS = {
    'admin': ['crear_usuario', 'eliminar_usuario', ...],
    'operator': ['registrar', 'borrar_registros', ...],
    'viewer': ['ver_historico', 'ver_incidencias']
}

# NUEVO: Decorador de protección por permisos
@require_permission('registrar')
def entrega():
    ...
```

### Nuevas Rutas:

| Ruta | Método | Autenticación | Descripción |
|------|--------|---------------|-------------|
| `/login` | GET, POST | ❌ Pública | Página de login |
| `/logout` | GET | ✅ Requerida | Cierra sesión |
| `/administracion` | GET | ✅ Admin | Panel administrativo |
| `/usuarios/crear` | GET, POST | ✅ Admin | Crear usuario |
| `/usuarios/<id>/editar` | GET, POST | ✅ Admin | Editar usuario |
| `/usuarios/<id>/eliminar` | POST | ✅ Admin | Eliminar usuario |

### Rutas Protegidas (Existentes):

Todas las rutas de negocio requieren autenticación:
- `/entrega` → require_permission('registrar')
- `/recepcion` → require_permission('registrar')
- `/incidencia` → require_permission('registrar')
- `/history` → require_permission('ver_historico')
- `/incidents` → require_permission('ver_incidencias')
- `/import` → require_permission('registrar')

## 📊 Base de Datos Actualizada

### Nueva Tabla: `usuarios`

```sql
+--------+----------+----------+--------+--------+------------------+
|   id   | username | password |  rol   | activo | fecha_creacion   |
+--------+----------+----------+--------+--------+------------------+
|   1    |  admin   | [hash]   | admin  |   1    | 2026-02-05T...   |
+--------+----------+----------+--------+--------+------------------+
```

### Tablas Existentes (Inalteradas):
- `entregas` - Registros de entregas/recepciones
- `incidencias` - Reportes de incidencias

## 🔄 Flujo de Autenticación

```
1. Usuario accede → /
   ↓
2. Redirecciona a → /login (si no está autenticado)
   ↓
3. Ingresa credenciales → POST /login
   ↓
4. Valida hash de contraseña
   ↓
5. Se crea sesión con Flask-Login
   ↓
6. Redirige a → /
   ↓
7. Usuario puede acceder según sus permisos
```

## 📚 Archivos de Documentación

### `AUTENTICACION.md`
- Sistema de roles completo
- Tabla de permisos
- Guía de administración
- Troubleshooting

### `INICIO_RAPIDO.md`
- Paso a paso para empezar
- Ejemplos de uso
- Problemas comunes
- Consejos prácticos

### `RESUMEN_IMPLEMENTACION.md`
- Cambios técnicos
- Descripción de seguridad
- Características implementadas

## ⚙️ Configuración Importante

En `app.py`, línea ~90:
```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

✅ **DEBE cambiar** esta clave antes de desplegar en producción.

## 🚀 Cómo Instalar/Actualizar

1. **Actualizar dependencias:**
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Base de datos:**
   - Si es primera vez: se crea automáticamente con tabla `usuarios`
   - Si ya existe: se añade tabla `usuarios` automáticamente
   - El usuario admin se crea automáticamente

3. **Ejecutar:**
   ```bash
   python app.py
   ```

## 🔐 Seguridad

✅ **Implementado:**
- Contraseñas hasheadas con PBKDF2
- Sesiones seguras
- CSRF protection implícito
- Validación de roles por ruta

⚠️ **Considera agregar:**
- HTTPS en producción
- Rate limiting para login
- Auditoría de cambios
- 2FA (autenticación de dos factores)

---

**Última actualización:** 5 de febrero de 2026
