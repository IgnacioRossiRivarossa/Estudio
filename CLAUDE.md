# CLAUDE.md — Estudio Rivarossa y Asociados · Sistema de Autogestión

Sistema web interno de gestión para el estudio contable, desarrollado con Django 5.2 full-stack (templates + Bootstrap). Incluye autenticación por invitación, roles, cuentas corrientes de clientes e indicadores económicos en tiempo real.

> **Antes de escribir cualquier código**, leer:
> `skills/django-fullstack/SKILL.md`

---

## Estructura del proyecto

```
Estudio/                          ← directorio raíz de trabajo (cd aquí para todo)
├── manage.py
├── requirements.txt
├── runtime.txt                   # python-3.11.8
├── render.yaml                   # Configuración declarativa de Render
├── build.sh                      # Build para Render: deps + collectstatic + migrate
├── run.sh                        # Inicia Gunicorn en producción
├── .env                          # Variables de entorno — NO subir al repo
│
├── Estudio/                      # Configuración central Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── usuarios/                     # Auth, roles, invitación, perfil
│   ├── backends.py               # Autenticación por email (no username)
│   ├── managers.py               # Manager personalizado de User
│   ├── models.py                 # Usuario + TokenActivacion
│   ├── signals.py                # Envío automático de emails al crear usuario
│   ├── validators.py             # Validadores de contraseña
│   ├── forms.py
│   ├── views.py
│   └── urls.py
│
├── clientes/                     # Empresas/clientes
│   ├── models.py                 # Empresa con validación CUIT argentino
│   └── admin.py
│
├── cotizaciones/                 # Indicadores económicos (sin modelos propios)
│   ├── services.py               # Consumo de APIs externas (dólar, inflación, UVA, riesgo país)
│   ├── views.py
│   ├── urls.py
│   └── templatetags/
│       └── cotizaciones_tags.py
│
├── cuentas_corrientes/           # Seguimiento de deudas de clientes
│   ├── models.py                 # ClienteCC, MesCC, ConfiguracionMeses
│   ├── views.py                  # Lista, edición AJAX, nuevo mes, exportar, importar
│   ├── urls.py
│   └── templatetags/
│       └── cc_tags.py
│
├── templates/
│   ├── base.html                 # Layout base: navbar + footer
│   ├── home.html                 # Dashboard principal
│   ├── 404.html / 500.html
│   ├── cotizaciones/
│   ├── cuentas_corrientes/
│   ├── usuarios/
│   └── email/                   # Templates de emails transaccionales
│
├── static/
│   ├── css/
│   │   ├── variables.css         # Design tokens del sistema de diseño
│   │   ├── components.css        # Componentes reutilizables
│   │   └── ...
│   └── js/
│       ├── cotizaciones.js       # Gráficos Chart.js del dashboard económico
│       ├── cuentas_corrientes.js # Edición inline AJAX de la tabla CC
│       └── ...
│
└── media/                        # Archivos subidos por usuarios
```

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Django 5.2 / Python 3.11.8 |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons + Chart.js |
| Archivos estáticos | Whitenoise + Brotli |
| Servidor | Gunicorn |
| Hosting | Render |
| Excel | openpyxl |
| Imágenes | Pillow |
| Config | python-decouple + dj-database-url |

---

## Comandos esenciales

> Todos los comandos se ejecutan desde `Estudio/` (donde está `manage.py`).

```bash
# Setup inicial en entorno nuevo
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Linux/macOS
pip install -r requirements.txt

# Configurar .env (ver sección Variables de entorno)

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # solicita: email, nombre, apellido, contraseña
python manage.py collectstatic --noinput
python manage.py runserver         # → http://localhost:8000

# Generar SECRET_KEY segura
python -c "from django.utils.crypto import get_random_string; print(get_random_string(50))"
```

---

## Variables de entorno

Crear `Estudio/.env` — **nunca subir al repositorio**.

```env
SECRET_KEY=genera-una-clave-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CSRF (solo producción con HTTPS)
# CSRF_TRUSTED_ORIGINS=https://tu-dominio.onrender.com

# Base de datos (producción)
DATABASE_URL=postgresql://user:password@localhost/dbname

# Email — Outlook SMTP
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@outlook.com
EMAIL_HOST_PASSWORD=tu-contraseña
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=tu-email@outlook.com
```

> Con `DEBUG=True` y sin credenciales de email, los correos se imprimen en consola (backend `console`).
> En producción, `SECRET_KEY` y `DATABASE_URL` los genera/provee Render automáticamente via `render.yaml`.

---

## Roles y accesos

| Rol | Descripción | Acceso clave |
|---|---|---|
| `Administrador` | Acceso completo + panel `/admin/` | Todo |
| `Colaborador` | Dashboard con funcionalidades limitadas | `/cotizaciones/`, `/cuentas-corrientes/` |
| `Cliente` | Solo su panel y empresas asociadas | Panel propio |

**El sistema de invitación funciona así:**
1. El admin crea el usuario desde `/admin/`
2. `signals.py` envía automáticamente un email con token de activación
3. El usuario activa su cuenta via `/activate/<token>/` y establece su contraseña
4. Token de recuperación de contraseña: expira a las **24 horas**
5. "Recordarme": sesión de **30 días**; sin él, sesión hasta cierre del navegador

---

## Apps y reglas de negocio críticas

### `usuarios`
- Identificador de login: **`email`** (no `username`). El campo `username` no se usa.
- El backend de autenticación está en `backends.py` — no modificar sin considerar el impacto en login.
- `TokenActivacion` es de **un solo uso**. Invalidarlo inmediatamente tras ser consumido.
- Políticas de contraseña (en `validators.py`): mínimo 8 chars, al menos una mayúscula, al menos un número, sin contraseñas comunes.

### `clientes`
- La gestión de empresas es **exclusiva del panel admin** (`/admin/`), no hay vistas propias.
- Validar siempre el **CUIT argentino**: formato `XX-XXXXXXXX-X` + dígito verificador.
- Relación M2M con `Usuario` (opcional en ambos lados). Estado: `activo` / `inactivo`.

### `cotizaciones`
- **Sin modelos propios** — consume APIs externas en `services.py`.
- APIs: `dolarapi.com` (cotizaciones) y `argentinadatos.com` (inflación, UVA, riesgo país).
- **Regla crítica:** si una API falla, el sistema **no debe lanzar excepción** — retornar lista vacía y loguear el error. Nunca propagar el error al usuario.
- Acceso restringido a roles `Administrador` y `Colaborador`.

### `cuentas_corrientes`
- Modelos: `ClienteCC` (cliente con `vencido` y `balance_especial`), `MesCC` (monto por período), `ConfiguracionMeses` (5 períodos activos).
- La tabla siempre muestra **exactamente 5 columnas mensuales** definidas en `ConfiguracionMeses`.
- **Nuevo mes — dos escenarios críticos:**
  - *Primera carga del mes:* rota la ventana → acumula mes más antiguo en `vencido`, lo elimina, crea nueva columna.
  - *Carga adicional del mismo mes:* suma montos al período existente, **sin rotar**.
  - Validar que la carga solo pueda hacerse durante el **mes calendario correspondiente**.
- **Importación masiva** (`/importar/`): solo `Administrador` con `is_staff=True`.
- La edición inline de filas usa **AJAX** — respetar la interfaz de respuesta JSON esperada por `cuentas_corrientes.js`.
- Exportación e importación usan **openpyxl** con formato `.xlsx`.

---

## URLs del sistema

| URL | Acceso |
|---|---|
| `/` | Redirige a `/login/` |
| `/login/` `/logout/` | Público / Autenticado |
| `/dashboard/` | Requiere login |
| `/perfil/` | Requiere login |
| `/activate/<token>/` | Enlace por email |
| `/password-reset/` `/password-reset-confirm/<token>/` | Público |
| `/cotizaciones/` | Administrador / Colaborador |
| `/cuentas-corrientes/` y subrutas | Administrador / Colaborador |
| `/cuentas-corrientes/importar/` | Solo Administrador (staff) |
| `/admin/` | Staff (`is_staff=True`) |

---

## Frontend (templates + static)

- **No hay API REST** — todo el frontend usa templates Django con renderizado server-side.
- Excepción: la edición inline de cuentas corrientes usa **AJAX** (`cuentas_corrientes.js` + endpoint `/cuentas-corrientes/editar/`).
- Sistema de diseño definido en `static/css/variables.css` — usar esas variables CSS al agregar estilos, no hardcodear colores ni tamaños.
- Componentes reutilizables en `static/css/components.css` — revisar antes de crear estilos nuevos.
- Gráficos con **Chart.js** (cotizaciones): no agregar otra librería de gráficos.
- Base de todos los templates: `templates/base.html` — extender siempre de él.

---

## Despliegue en Render

El `render.yaml` define el servicio y la base de datos PostgreSQL declarativamente. Variables configuradas automáticamente por Render: `SECRET_KEY`, `DATABASE_URL`, `RENDER`.

Variables a configurar manualmente en el panel de Render:

| Variable | Descripción |
|---|---|
| `EMAIL_HOST_USER` | Email Outlook para notificaciones |
| `EMAIL_HOST_PASSWORD` | App Password del email |
| `DEFAULT_FROM_EMAIL` | Email remitente visible |
| `CSRF_TRUSTED_ORIGINS` | `https://tu-dominio.onrender.com` |

Para cambiar contraseña del superusuario inicial via Shell de Render:
```bash
python manage.py changepassword <email>
```

---

## Seguridad en producción (activada cuando `RENDER=true`)

- HTTPS forzado con redirección SSL
- HSTS: 1 año, subdomains, preload
- Cookies: `Secure`, `HttpOnly`, `SameSite=Lax`
- `X_FRAME_OPTIONS = DENY`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `DEBUG = False` automático al detectar variable de entorno `RENDER`
