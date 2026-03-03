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
├── cotizaciones/                # App de indicadores económicos (sin modelos propios)
│   ├── services.py              # Consumo de APIs externas (dólar, inflación, UVA, riesgo país)
│   ├── urls.py
│   ├── views.py
│   └── templatetags/
│       └── cotizaciones_tags.py
│
├── cuentas_corrientes/          # App de cuentas corrientes
│   ├── models.py                # ClienteCC, MesCC, ConfiguracionMeses
│   ├── urls.py
│   ├── views.py                 # Lista, edición AJAX, nuevo mes, exportar, importar
│   └── templatetags/
│       └── cc_tags.py
│
├── templates/
│   ├── base.html                # Layout base (navbar, footer)
│   ├── home.html                # Dashboard principal
│   ├── 404.html
│   ├── 500.html
│   ├── cotizaciones/
│   │   └── dashboard.html       # Dashboard de indicadores económicos
│   ├── cuentas_corrientes/
│   │   ├── lista.html           # Tabla principal con edición inline
│   │   ├── nuevo_mes.html       # Carga de facturación mensual por Excel
│   │   └── importar.html        # Importación masiva inicial (solo admin+staff)
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
│   │   ├── custom.css
│   │   ├── auth.css
│   │   └── pages.css
│   ├── js/
│   │   ├── main.js
│   │   ├── cotizaciones.js      # Gráficos y lógica del dashboard económico
│   │   ├── cuentas_corrientes.js# Edición inline y lógica de la tabla CC
│   │   ├── auth.js
│   │   └── password-validation.js
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

### Dashboard Económico

Accesible para roles **Administrador** y **Colaborador** en `/cotizaciones/`.

Muestra en tiempo real datos obtenidos de APIs públicas argentinas:

| Fuente | Datos |
|---|---|
| [dolarapi.com](https://dolarapi.com) | Cotizaciones del dólar (oficial, blue, MEP, CCL, cripto, etc.) y otras divisas |
| [argentinadatos.com](https://api.argentinadatos.com) | Inflación mensual e interanual, índice UVA, riesgo país |

**Componentes del dashboard:**
- Cards resumen: cotizaciones del dólar por tipo, última inflación mensual e interanual, último UVA, riesgo país
- Gráfico de inflación mensual (últimos 24 meses, Chart.js)
- Gráfico de inflación interanual (últimos 24 meses, Chart.js)
- Gráfico de evolución del UVA (últimos 60 meses, Chart.js)
- Gráfico de riesgo país (últimos 60 meses, Chart.js)

Si una API no responde, el sistema no falla: devuelve una lista vacía y registra el error en el log.

### Cuentas Corrientes

Accesible para roles **Administrador** y **Colaborador** en `/cuentas-corrientes/`.

Módulo de seguimiento de deudas periódicas de clientes, con estructura de hasta 5 columnas mensuales configurables.

#### Modelos

| Modelo | Descripción |
|---|---|
| `ClienteCC` | Cliente con nombre único, campo `vencido` (deuda acumulada histórica), `balance_especial` (editable manualmente) y propiedad calculada `saldo` |
| `MesCC` | Registro mensual de un cliente: `periodo` (día 1 del mes) y `monto`. Restricción única `(cliente, periodo)` |
| `ConfiguracionMeses` | Define los 5 periodos activos visibles en la tabla. Orden 1 = más antiguo, 5 = más reciente |

#### Funcionalidades

**Lista (`/cuentas-corrientes/`)**
- Tabla paginada (50 por página) de clientes activos con columnas: Vencido, Balance/Especial y los 5 meses activos
- Saldo total calculado dinámicamente
- Búsqueda por nombre
- Ordenamiento por nombre (defecto) o por saldo (ascendente / descendente)
- Fila de totales por columna al pie
- Edición inline por fila vía AJAX (sin recargar la página)
- Exportar a Excel con formato estilag (.xlsx)

**Nuevo Mes (`/cuentas-corrientes/nuevo-mes/`)**  
Carga una facturación mensual desde un archivo `.xlsx` (dos columnas: Nombre, Monto).

- **Escenario 1 — Primera carga del mes:** desplaza la ventana de 5 meses: acumula el mes más antiguo en `vencido`, lo elimina y crea la nueva columna con los montos del Excel
- **Escenario 2 — Carga adicional del mismo mes:** suma los montos al periodo ya existente sin rotar columnas
- Crea automáticamente clientes nuevos si el nombre no existe
- Valida que el proceso solo pueda ejecutarse durante el mes calendario correspondiente

**Importar (`/cuentas-corrientes/importar/`) — Solo Administrador + staff**  
Importación masiva inicial desde un `.xlsx` con el mismo formato que la exportación:
`Cliente | Saldo (ignorado) | Vencido | Balance/Especial | Mes1 | ... | MesN`
- Crea o actualiza clientes y registros de meses
- Configura automáticamente los periodos en `ConfiguracionMeses`

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
| `/` | — | Redirige a `/login/` |
| `/login/` | `login` | Público |
| `/logout/` | `logout` | Autenticado |
| `/dashboard/` | `dashboard` | Requiere login |
| `/perfil/` | `perfil` | Requiere login |
| `/activate/<token>/` | `activate` | Enlace por email |
| `/password-reset/` | `password_reset` | Público |
| `/password-reset-confirm/<token>/` | `password_reset_confirm` | Enlace por email |
| `/cotizaciones/` | `cotizaciones:dashboard_economico` | Administrador / Colaborador |
| `/cuentas-corrientes/` | `cuentas_corrientes:lista` | Administrador / Colaborador |
| `/cuentas-corrientes/editar/` | `cuentas_corrientes:editar_fila` | Administrador / Colaborador |
| `/cuentas-corrientes/nuevo-mes/` | `cuentas_corrientes:nuevo_mes` | Administrador / Colaborador |
| `/cuentas-corrientes/exportar/` | `cuentas_corrientes:exportar` | Administrador / Colaborador |
| `/cuentas-corrientes/importar/` | `cuentas_corrientes:importar` | Administrador (staff) |
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