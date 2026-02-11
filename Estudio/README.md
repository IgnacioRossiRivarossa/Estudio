# Estudio - Sistema de Gestión Empresarial

Sistema de gestión empresarial desarrollado con Django 5.2, diseñado para la administración de clientes, empresas y colaboradores. Incluye sistema de autenticación por invitación, gestión de roles y preparado para despliegue en Render.

## Tecnologías Utilizadas

- **Backend:** Django 5.2 / Python 3.11.8
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend:** Bootstrap 5.3, Bootstrap Icons
- **Servidor:** Gunicorn
- **Hosting:** Render
- **Archivos estáticos:** Whitenoise

## Requisitos del Sistema

- Python 3.11.8
- pip (gestor de paquetes de Python)
- Git

## Instalación Local (Paso a Paso)

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Estudio
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Copiar el archivo de ejemplo y editar con tus valores:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:
```
SECRET_KEY=una-clave-secreta-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=tu-email@outlook.com
EMAIL_HOST_PASSWORD=tu-password
```

> **Nota:** En modo DEBUG si no configuras credenciales de email, los emails se mostrarán en la consola.

### 6. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

Se te pedirá:
- Email
- Nombre
- Apellido
- Contraseña

### 8. Recolectar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 9. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

El proyecto estará disponible en: `http://localhost:8000`

## Estructura del Proyecto

```
Estudio/
├── manage.py                    # Utilidad de línea de comandos de Django
├── requirements.txt             # Dependencias del proyecto
├── runtime.txt                  # Versión de Python para Render
├── render.yaml                  # Configuración de despliegue en Render
├── .env.example                 # Ejemplo de variables de entorno
├── .gitignore                   # Archivos ignorados por Git
├── README.md                    # Este archivo
│
├── Estudio/                     # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py              # Configuración de Django
│   ├── urls.py                  # URLs raíz del proyecto
│   ├── wsgi.py                  # Configuración WSGI (producción)
│   └── asgi.py                  # Configuración ASGI
│
├── usuarios/                    # App de gestión de usuarios
│   ├── __init__.py
│   ├── admin.py                 # Configuración del admin
│   ├── apps.py                  # Configuración de la app
│   ├── backends.py              # Backend de autenticación por email
│   ├── forms.py                 # Formularios (login, contraseña, etc.)
│   ├── managers.py              # Manager personalizado del modelo Usuario
│   ├── models.py                # Modelos (Usuario, TokenActivacion)
│   ├── signals.py               # Señales (envío automático de emails)
│   ├── urls.py                  # URLs de la app
│   ├── validators.py            # Validadores de contraseña personalizados
│   └── views.py                 # Vistas (login, activación, etc.)
│
├── clientes/                    # App de gestión de clientes/empresas
│   ├── __init__.py
│   ├── admin.py                 # Configuración del admin
│   ├── apps.py                  # Configuración de la app
│   └── models.py                # Modelo Empresa con validación CUIT
│
├── templates/                   # Templates HTML
│   ├── base.html                # Template base con Bootstrap 5
│   ├── home.html                # Dashboard principal
│   ├── 404.html                 # Página de error 404
│   ├── 500.html                 # Página de error 500
│   ├── usuarios/
│   │   ├── login.html           # Página de login
│   │   ├── activate.html        # Activación de cuenta
│   │   ├── password_reset.html  # Solicitar recuperación
│   │   └── password_reset_confirm.html  # Nueva contraseña
│   ├── email/
│   │   ├── activacion_cuenta.html       # Email de activación
│   │   └── recuperacion_password.html   # Email de recuperación
│   └── clientes/                # Templates de clientes (futuro)
│
├── static/                      # Archivos estáticos
│   ├── css/custom.css           # CSS personalizado
│   ├── js/main.js               # JavaScript principal
│   ├── img/                     # Imágenes (logo, favicon)
│   └── robots.txt               # Archivo robots.txt
│
└── media/                       # Archivos subidos por usuarios
```

## Funcionalidades

### Sistema de Autenticación
- **Login por email** (sin username)
- **Sistema de invitación:** El administrador crea usuarios desde el panel admin
- **Activación por email:** Se envía un enlace para establecer contraseña
- **Recuperación de contraseña:** Flujo completo con token de seguridad
- **Tokens con expiración:** 24 horas de validez

### Roles de Usuario
- **Administrador:** Acceso completo al sistema y panel admin
- **Colaborador:** Acceso al dashboard con funcionalidades limitadas
- **Cliente:** Acceso a su panel personal y empresas asociadas

### Gestión de Empresas
- CRUD desde el panel admin
- Validación de CUIT argentino
- Asociación de usuarios a empresas
- Estados: activo/inactivo

### Políticas de Contraseña
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos un número
- Validación en tiempo real en el frontend

## Despliegue en Render

### Archivos de Deploy
El proyecto incluye los siguientes archivos para facilitar el despliegue:

- **`build.sh`**: Script de construcción que instala dependencias, recolecta archivos estáticos, ejecuta migraciones y crea el superusuario inicial.
- **`run.sh`**: Script que ejecuta el servidor Gunicorn en producción.
- **`render.yaml`**: Configuración automática para Render (detecta automáticamente el proyecto).

### Paso a Paso

### 1. Crear cuenta en Render
Visita [render.com](https://render.com) y crea una cuenta gratuita.

### 2. Conectar repositorio
- Ve a Dashboard → New → Web Service
- Conecta tu repositorio de GitHub/GitLab
- Selecciona el repositorio del proyecto

### 3. Configuración automática
Render detectará automáticamente el archivo `render.yaml` y configurará:
- Base de datos PostgreSQL
- Variables de entorno
- Comandos de build y start

### 4. Configurar variables de entorno secretas
En el panel de Render, configura estas variables (las marcadas como `sync: false`):

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `EMAIL_HOST_USER` | `tu-email@outlook.com` | Email para envío de notificaciones |
| `EMAIL_HOST_PASSWORD` | `tu-contraseña` | Contraseña del email (usar contraseña de aplicación) |
| `DEFAULT_FROM_EMAIL` | `tu-email@outlook.com` | Email que aparece como remitente |

**Nota:** `SECRET_KEY`, `DATABASE_URL` y `RENDER` se configuran automáticamente.

### 5. Deploy
- Haz clic en "Create Web Service"
- Render ejecutará automáticamente `build.sh` (instalación y migraciones)
- Luego ejecutará `run.sh` (servidor Gunicorn)

### 6. Acceder al superusuario
El script `build.sh` crea automáticamente un superusuario con:
- **Username:** `admin`
- **Email:** `ignaciorossi@rivarossa.com`
- **Contraseña:** Establecer desde el shell de Render

Para establecer la contraseña, ve a Shell en Render y ejecuta:
```bash
python manage.py changepassword admin
```

### 7. Configurar dominio personalizado (opcional)
En Settings → Custom Domain, puedes agregar tu propio dominio.

## URLs Principales

| URL | Descripción | Acceso |
|-----|-------------|--------|
| `/` | Dashboard | Requiere login |
| `/login/` | Inicio de sesión | Público |
| `/logout/` | Cerrar sesión | Autenticado |
| `/activate/<token>/` | Activar cuenta | Enlace por email |
| `/password-reset/` | Solicitar recuperación | Público |
| `/password-reset-confirm/<token>/` | Nueva contraseña | Enlace por email |
| `/admin/` | Panel de administración | Staff |

## Licencia

Este proyecto es de uso privado.
