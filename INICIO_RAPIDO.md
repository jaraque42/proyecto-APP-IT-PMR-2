# 🚀 GUÍA DE INICIO RÁPIDO - Sistema de Autenticación

## Instalación

1. **Instalar dependencias:**
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

3. **Acceder a la aplicación:**
   - Abre tu navegador en: `http://localhost:5000`

## Login Inicial

| Campo | Valor |
|-------|-------|
| Usuario | `admin` |
| Contraseña | `admin123` |
| Rol | Admin (acceso completo) |

## Pasos Iniciales Recomendados

### 1️⃣ Cambiar la Contraseña del Admin (IMPORTANTE)
- Si los datos están un poco sensibles, considera cambiar la contraseña
- Por ahora, puedes mantenerla o crear usuarios adicionales

### 2️⃣ Crear Usuarios Operadores
1. Haz clic en "Administración" en la esquina superior
2. Haz clic en "+ Crear Usuario"
3. Llena los campos:
   - **Nombre de Usuario:** (ej. `juan`)
   - **Contraseña:** (mínimo 6 caracteres)
   - **Rol:** Selecciona "OPERATOR" para que pueda registrar pero no borrar todo
4. Haz clic en "Crear Usuario"

### 3️⃣ Crear Usuarios Lectores (Opcional)
- Mismo proceso pero selecciona rol "VIEWER"
- Estos usuarios solo pueden ver datos, no modificarlos

## 📋 Roles Explicados

### 👨‍💼 ADMIN
Puede hacer **todo**:
- ✅ Crear y eliminar usuarios
- ✅ Registrar entregas
- ✅ Registrar recepciones  
- ✅ Reportar incidencias
- ✅ Ver histórico
- ✅ Borrar registros
- ✅ Exportar Excel

### 👷 OPERATOR
Puede registrar y borrar:
- ✅ Registrar entregas
- ✅ Registrar recepciones
- ✅ Reportar incidencias
- ✅ Ver histórico
- ✅ Borrar registros
- ❌ No puede crear usuarios

### 👁️ VIEWER
Solo visualizar:
- ✅ Ver histórico
- ✅ Ver incidencias
- ✅ Exportar Excel
- ❌ No puede registrar
- ❌ No puede borrar

## 🔑 Gestión de Contraseñas

### ¿Olvidé la contraseña de admin?
1. Detén la aplicación (Ctrl+C)
2. Elimina el archivo `entregas.db`
3. Reinicia la aplicación
4. Las credenciales volverán a ser `admin` / `admin123`

### ¿Olvidé la contraseña de otro usuario?
1. Inicia sesión como admin
2. Ve a "Administración"
3. Edita al usuario y guarda cambios (se puede resetear)
4. O elmina y crea uno nuevo

## 📱 Flujo Típico de Uso

### Para un OPERATOR:

```
1. Abre http://localhost:5000
2. Ingresa tu usuario y contraseña
3. La página principal te muestra 3 opciones:
   - Entrega: Registra un nuevo dispositivo
   - Recepción: Registra devolución de dispositivo
   - Incidencias: Reporta problemas
4. Haz clic en "Histórico" para ver lista de registros
5. Puedes exportar a Excel o buscar específicos
6. Haz clic en "Cerrar Sesión" cuando termines
```

### Para un ADMIN:

```
1. Todo lo del OPERATOR +
2. Puedes acceder a "Administración"
3. Aquí puedes:
   - Ver lista de usuarios
   - Crear nuevos usuarios
   - Editar roles
   - Desactivar o eliminar usuarios
```

## 🆘 Problemas Comunes

### "Usuario o contraseña incorrectos"
- Verifica que escribiste exactamente igual (mayúsculas/minúsculas importan)
- Comprueba que el usuario está activo en Administración
- Prueba con `admin` / `admin123` para verificar que el sistema funciona

### "No tienes permisos para esta acción"
- Tu rol actual no permite esa acción
- Pide a un admin que expanda tus permisos
- O usa una cuenta con rol más alto

### "Página no encontrada" 
- Asegúrate que la aplicación está corriendo: `python app.py`
- Verifica la URL: debe ser `http://localhost:5000` (no `localhost:5000` a secas)

### La aplicación no inicia
- Instala las dependencias: `python -m pip install -r requirements.txt`
- Asegúrate de tener Python 3.7+: `python --version`

## 💡 Consejos de Uso

✅ **Deber:**
- Contacta al admin si necesitas permisos adicionales
- Cierra sesión cuando termines
- Usa contraseñas fuertes (>8 caracteres, con números y símbolos)

❌ **No deber:**
- Compartir contraseñas
- Dejar la sesión activa en dispositivos públicos
- Usar roles admin para tareas de operación regular

## 📞 Soporte

Si encuentras problemas:
1. Revisa la documentación en `AUTENTICACION.md`
2. Verifica que todas las dependencias están instaladas
3. Reinicia la aplicación
4. Comprueba que el archivo `entregas.db` existe y tiene permisos de lectura/escritura

---

**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Estado:** ✅ Funcionando
