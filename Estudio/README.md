# Estudio Rivarossa y Asociados — Sistema de Autogestión

Sistema web de gestión interna desarrollado con Django 5.2, orientado a la administración de clientes empresariales, usuarios y colaboradores del estudio. Incluye autenticación por invitación, gestión de roles, perfil de usuario y está preparado para despliegue en Render.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Django 5.2 / Python 3.11.8 |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| Archivos estáticos | Whitenoise + Brotli |
| Servidor | Gunicorn |
| Hosting | Render |

## Requisitos

- Python 3.11.8
- pip
- Git

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone 
cd Estudio
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear el archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
SECRET_KEY=genera-una-clave-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Orígenes de confianza para CSRF (solo producción con HTTPS)
# CSRF_TRUSTED_ORIGINS=https://tu-dominio.com

DATABASE_URL=postgresql://user:password@localhost/dbname

EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@outlook.com
EMAIL_HOST_PASSWORD=tu-contraseña
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=tu-email@outlook.com
```

> En modo `DEBUG=True`, si no configurás credenciales de email, los correos se imprimen en consola automáticamente.

> Para generar un `SECRET_KEY` seguro:
> ```bash
> python -c "from django.utils.crypto import get_random_string; print(get_random_string(50))"
> ```

### 5. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

Se solicitarán: email, nombre, apellido y contraseña.

### 7. Recolectar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Disponible en: `http://localhost:8000`

---

## Estructura del proyecto

```
Estudio/
├── manage.py
├── requirements.txt
├── runtime.txt                  # Versión de Python para Render
├── render.yaml                  # Configuración de despliegue en Render
├── build.sh                     # Script de build para Render
├── run.sh                       # Script de inicio para Render
├── .env                         # Variables de entorno (no subir al repo)
├── .gitignore
├── README.md
│
├── Estudio/                     # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── usuarios/                    # App de usuarios
│   ├── admin.py
│   ├── backends.py              # Autenticación por email
│   ├── forms.py                 # Login, contraseña, recuperación
│   ├── managers.py              # Manager personalizado
│   ├── models.py                # Usuario, TokenActivacion
│   ├── signals.py               # Envío automático de emails
│   ├── urls.py
│   ├── validators.py            # Validadores de contraseña
│   └── views.py                 # Login, perfil, activación, etc.
│
├── clientes/                    # App de empresas/clientes
│   ├── admin.py
│   └── models.py                # Empresa con validación CUIT
│
├── templates/
│   ├── base.html                # Layout base (navbar, footer)
│   ├── home.html                # Dashboard principal
│   ├── landing.html             # Página pública
│   ├── 404.html
│   ├── 500.html
│   ├── usuarios/
│   │   ├── login.html
│   │   ├── perfil.html          # Perfil del usuario autenticado
│   │   ├── activate.html
│   │   ├── password_reset.html
│   │   └── password_reset_confirm.html
│   └── email/
│       ├── activacion_cuenta.html
│       └── recuperacion_password.html
│
├── static/
│   ├── css/
│   │   ├── variables.css        # Design system (tokens de diseño)
│   │   ├── components.css       # Componentes reutilizables
│   │   └── custom.css
│   ├── js/main.js
│   └── robots.txt
│
└── media/                       # Archivos subidos por usuarios
```

---

## Funcionalidades

### Autenticación
- Login por **email** (sin username)
- **Sistema de invitación:** el administrador crea usuarios desde el panel admin
- **Activación por email:** se envía un enlace con token para establecer contraseña inicial
- **Recuperación de contraseña:** flujo completo con token (expiración 24 hs)
- Opción "Recordarme" (sesión de 30 días) o sesión hasta cierre del navegador

### Roles
| Rol | Descripción |
|---|---|
| Administrador | Acceso completo + panel admin |
| Colaborador | Acceso al dashboard con funcionalidades limitadas |
| Cliente | Acceso a su panel y empresas asociadas |

### Perfil de usuario
- Vista de solo lectura accesible desde el menú superior derecho
- Muestra: nombre completo, email, rol, estado de cuenta y empresas asociadas activas

### Gestión de empresas
- Administración desde el panel admin (`/admin/`)
- Validación de **CUIT argentino** (formato + dígito verificador)
- Relación muchos a muchos con usuarios (opcional en ambos lados)
- Estados: activo / inactivo

### Políticas de contraseña
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos un número
- Sin contraseñas comunes

### Seguridad (producción)
- `HTTPS` forzado con redirección SSL
- `HSTS` con 1 año, subdomains y preload
- Cookies de sesión y CSRF: `Secure`, `HttpOnly`, `SameSite=Lax`
- `X_FRAME_OPTIONS = DENY`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `CSRF_TRUSTED_ORIGINS` configurable por variable de entorno

---

## URLs

| URL | Nombre | Acceso |
|---|---|---|
| `/` | `home` | Requiere login |
| `/login/` | `login` | Público |
| `/logout/` | `logout` | Autenticado |
| `/perfil/` | `perfil` | Requiere login |
| `/activate/<token>/` | `activate` | Enlace por email |
| `/password-reset/` | `password_reset` | Público |
| `/password-reset-confirm/<token>/` | `password_reset_confirm` | Enlace por email |
| `/admin/` | — | Staff (`is_staff=True`) |
| `/robots.txt` | — | Público |

---

## Despliegue en Render

### Archivos incluidos

- **`render.yaml`** — configuración declarativa del servicio y base de datos
- **`build.sh`** — instala dependencias, recolecta estáticos y ejecuta migraciones
- **`run.sh`** — inicia Gunicorn en producción
- **`runtime.txt`** — define la versión de Python (`python-3.11.8`)

### Pasos

1. Crear cuenta en [render.com](https://render.com)
2. **New → Web Service** → conectar repositorio de GitHub
3. Render detecta `render.yaml` automáticamente
4. Configurar las siguientes variables de entorno en el panel de Render:

| Variable | Descripción |
|---|---|
| `EMAIL_HOST_USER` | Email para envío de notificaciones |
| `EMAIL_HOST_PASSWORD` | Contraseña (preferentemente App Password) |
| `DEFAULT_FROM_EMAIL` | Email remitente visible por el usuario |
| `CSRF_TRUSTED_ORIGINS` | `https://tu-dominio.onrender.com` |

> `SECRET_KEY`, `DATABASE_URL` y `RENDER` se configuran automáticamente por Render.

5. Hacer clic en **Create Web Service**
6. Para cambiar la contraseña del superusuario inicial, usar el Shell de Render:

```bash
python manage.py changepassword <email>
```

---

## Licencia

Uso privado — Estudio Rivarossa y Asociados.