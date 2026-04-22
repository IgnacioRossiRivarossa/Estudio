# SKILL: Buenas prácticas — Django 5.2 Full-Stack con Templates
## Estudio Rivarossa y Asociados · Sistema de Autogestión

> **Leer este archivo completo antes de escribir cualquier línea de código.**
> Aplica a toda tarea que implique crear, modificar, revisar o extender código en este proyecto.
> No es opcional: es el contrato de calidad del proyecto.

---

## 0. Flujo de trabajo obligatorio antes de cualquier tarea

Antes de escribir código, seguir este flujo sin excepción:

1. **Leer `CLAUDE.md`** para entender el contexto del dominio, la estructura de apps y las reglas de negocio críticas.
2. **Leer este `SKILL.md`** completo.
3. **Explorar los archivos existentes** de la app afectada (`models.py`, `views.py`, `services.py`, `forms.py`, `urls.py`, templates relacionados) antes de modificar o crear cualquier cosa.
4. **Verificar si ya existe** lo que se necesita: un modelo, un service, un templatetag, un componente CSS. No reinventar lo que ya está construido.
5. **Planificar** qué archivos se van a tocar y por qué, antes de ejecutar.
6. **Implementar** siguiendo todas las reglas de este skill.
7. **Verificar el checklist** de la sección 13 antes de dar la tarea por terminada.

> Saltear cualquiera de estos pasos es la causa número uno de deuda técnica en este proyecto.

---

## 1. Filosofía transversal — no negociable

Todo el código de este proyecto respeta dos principios que aplican a cada decisión de diseño, sin excepción:

### Alta cohesión

Cada módulo, clase o función tiene **una única responsabilidad bien definida** y todo lo que contiene está directamente relacionado con esa responsabilidad.

Señales de alarma:
- Una función que hace más de una cosa (si el nombre necesita un "y", hay que partir).
- Un archivo `utils.py` genérico con funciones de dominios completamente distintos.
- Una vista que valida datos, llama a una API externa, procesa un Excel y renderiza un template.
- Una app que gestiona clientes, procesa pagos Y envía emails → tres responsabilidades, probablemente tres módulos.

### Bajo acoplamiento

Los módulos se conocen lo menos posible entre sí. Una app no debe importar los modelos internos de otra si puede evitarlo. Los servicios no conocen las vistas. Los modelos no conocen los formularios.

Señales de alarma:
- Una vista de `cuentas_corrientes` importando forms de `usuarios`.
- `cotizaciones` importando algo de `cuentas_corrientes`.
- Lógica de negocio duplicada en dos apps distintas.

### La pregunta de diseño antes de escribir código

Antes de ubicar cualquier pieza de código, hacerse estas tres preguntas:
1. ¿Este código pertenece realmente acá, o está invadiendo otra capa?
2. ¿Si modifico esto, cuántas otras partes del sistema se ven afectadas?
3. ¿Puedo testear este módulo de forma aislada, sin levantar el resto del sistema?

Si la respuesta a la tercera es "no", el diseño necesita revisión antes de continuar.

---

## 2. Arquitectura y separación de responsabilidades

### Estructura estándar por app

```
nombre_app/
├── models.py           # Modelos, validaciones DB, métodos de instancia, propiedades calculadas
├── views.py            # Recibe request → llama lógica → renderiza template o devuelve JSON
├── forms.py            # Formularios Django: validación y limpieza de entrada del usuario
├── urls.py             # Rutas de la app — siempre con namespace
├── admin.py            # Registro en panel admin — registrar TODOS los modelos desde el inicio
├── services.py         # Lógica de negocio compleja o integración con servicios externos
├── signals.py          # Signals para comunicación desacoplada entre apps
├── validators.py       # Validadores reutilizables (ej: CUIT argentino)
├── managers.py         # Managers personalizados de QuerySet
├── templatetags/
│   └── nombre_tags.py  # Tags y filtros custom para templates
├── migrations/
```

### Qué va dónde — tabla de responsabilidades

| Capa | Responsabilidad | Lo que NUNCA debe hacer |
|---|---|---|
| `models.py` | Estructura de datos, `clean()`, `@property`, `__str__`, managers | Llamadas HTTP, lógica de presentación, importar forms o views |
| `managers.py` | QuerySets reutilizables y semánticos del dominio | Lógica de presentación, efectos secundarios |
| `forms.py` | Validar y limpiar datos de entrada del usuario | Consultas pesadas, efectos secundarios, lógica de negocio |
| `validators.py` | Funciones de validación puras y reutilizables | Estado, efectos secundarios |
| `views.py` | Orquestar: autenticar → validar → llamar service/modelo → renderizar | Lógica de negocio directamente, queries complejos inline |
| `services.py` | Lógica compleja, APIs externas, operaciones multi-modelo | Renderizar templates, manejar requests, importar views |
| `signals.py` | Reacciones desacopladas a eventos del modelo | Lógica de negocio principal, UI |
| `templatetags/` | Filtros y tags para presentación en templates | Lógica de negocio, queries directos |
| `admin.py` | Configuración del panel de administración | Lógica de negocio |

### Flujo de dependencias — dirección única

```
views.py → forms.py
views.py → services.py → models.py
views.py → models.py (solo para queries simples)
templatetags/ → models.py (solo lectura)
signals.py → services.py → models.py
admin.py → models.py
```

**Nunca** invertir estas flechas. Si `services.py` necesita importar algo de `views.py`, el diseño está mal.

### Convención de nombres — español en el dominio

- Modelos: `PascalCase` singular → `ClienteCC`, `MesCC`, `ConfiguracionMeses`
- Campos DB: `snake_case` → `balance_especial`, `fecha_vencimiento`, `periodo`
- URLs: `kebab-case` → `/cuentas-corrientes/nuevo-mes/`
- Variables y funciones Python: `snake_case` → `cliente_activo`, `meses_configurados`
- Templates: `snake_case.html` → `nuevo_mes.html`, `lista_clientes.html`
- IDs y clases CSS/JS: `kebab-case` → `#tabla-clientes`, `.btn-editar-fila`
- Archivos JS: `snake_case.js` → `cuentas_corrientes.js`, `cotizaciones.js`
- Constantes: `UPPER_SNAKE_CASE` → `TIMEOUT_SEGUNDOS = 5`

---

## 3. Modelos Django

### Modelo bien construido — plantilla de referencia

```python
import logging
from django.db import models
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ClienteCC(models.Model):
    """
    Representa un cliente en el sistema de cuentas corrientes.

    El saldo total es la suma de vencido + balance_especial + meses activos.
    Los meses activos se definen en ConfiguracionMeses (siempre 5 períodos).
    """

    nombre = models.CharField(max_length=200, unique=True)
    vencido = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_especial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente CC'
        verbose_name_plural = 'Clientes CC'

    def __str__(self):
        return self.nombre

    @property
    def saldo_total(self):
        """Saldo total: vencido + balance_especial + suma de meses activos."""
        from django.db.models import Sum
        meses = self.meses.aggregate(total=Sum('monto'))['total'] or 0
        return self.vencido + self.balance_especial + meses

    @property
    def tiene_deuda_vencida(self):
        """True si el cliente tiene saldo vencido mayor a cero."""
        return self.vencido > 0

    def clean(self):
        """Validaciones de integridad de negocio — no duplicar en la vista."""
        if self.vencido < 0:
            raise ValidationError({'vencido': 'El saldo vencido no puede ser negativo.'})
        if self.balance_especial < 0:
            raise ValidationError({'balance_especial': 'El balance especial no puede ser negativo.'})
```

### Reglas para modelos

- **Siempre** definir `__str__`, `class Meta` con `ordering`, `verbose_name` y `verbose_name_plural`.
- Usar `auto_now_add=True` para `fecha_creacion`, `auto_now=True` para `fecha_actualizacion` — en todos los modelos que registren auditoría.
- Propiedades calculadas que combinan campos van como `@property`, no como campos de DB.
- Validaciones de negocio en `clean()` — Django las ejecuta en formularios y en `full_clean()`.
- **Nunca** usar `null=True` en `CharField`/`TextField`; usar `blank=True, default=''`.
- Restricciones únicas compuestas: usar `class Meta: constraints` o `unique_together`.
- Los `choices` como constantes de clase, no strings hardcodeados dispersos.
- Docstring en cada modelo explicando su propósito y relaciones clave.
- Managers personalizados en `managers.py`, no inline en `models.py`.

```python
# Choices como constantes de clase — extensibles sin romper código que las consume
class Usuario(AbstractBaseUser):
    class Rol(models.TextChoices):
        ADMINISTRADOR = 'Administrador', 'Administrador'
        COLABORADOR = 'Colaborador', 'Colaborador'
        CLIENTE = 'Cliente', 'Cliente'

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.COLABORADOR)
```

```python
# Restricción de unicidad compuesta
class MesCC(models.Model):
    cliente = models.ForeignKey(ClienteCC, on_delete=models.CASCADE, related_name='meses')
    periodo = models.DateField()  # Siempre día 1 del mes — invariante del sistema

    class Meta:
        unique_together = [('cliente', 'periodo')]
        ordering = ['periodo']
        verbose_name = 'Mes CC'
        verbose_name_plural = 'Meses CC'
```

### Managers personalizados

```python
# cuentas_corrientes/managers.py
from django.db import models


class ClienteCCQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(activo=True)

    def con_deuda_vencida(self):
        return self.filter(vencido__gt=0)

    def ordenados_por_saldo(self):
        """Ordenar por saldo total requiere anotación — no usar @property en queryset."""
        from django.db.models import Sum, F, Coalesce, Value
        from decimal import Decimal
        return self.annotate(
            saldo_anotado=Coalesce(Sum('meses__monto'), Value(Decimal('0')))
                          + F('vencido') + F('balance_especial')
        ).order_by('-saldo_anotado')


class ClienteCCManager(models.Manager):
    def get_queryset(self):
        return ClienteCCQuerySet(self.model, using=self._db)

    def activos(self):
        return self.get_queryset().activos()
```

---

## 4. Vistas Django (full-stack con templates)

### Vista estándar con formulario — plantilla PRG

```python
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError

from .forms import NuevoMesForm
from .services import procesar_nuevo_mes

logger = logging.getLogger(__name__)


@login_required
def nuevo_mes(request):
    """
    Procesa la carga de un nuevo período de cuentas corrientes via archivo Excel.
    Acceso restringido a Administrador y Colaborador.
    """
    _verificar_rol(request.user, ['Administrador', 'Colaborador'])

    if request.method == 'POST':
        form = NuevoMesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resultado = procesar_nuevo_mes(form.cleaned_data['archivo'])
                messages.success(
                    request,
                    f'Se procesaron {resultado["filas"]} registros correctamente.'
                )
                return redirect('cuentas_corrientes:lista')  # PRG — siempre redirigir tras POST exitoso
            except ValidationError as e:
                form.add_error(None, e)
            except Exception as e:
                logger.exception(f'Error inesperado al procesar nuevo mes: {e}')
                messages.error(request, 'Ocurrió un error inesperado. Por favor, intentá de nuevo.')
    else:
        form = NuevoMesForm()

    return render(request, 'cuentas_corrientes/nuevo_mes.html', {'form': form})
```

### Vista AJAX — contrato JSON

```python
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import ClienteCC

logger = logging.getLogger(__name__)


@login_required
@require_POST
def editar_fila(request):
    """
    Endpoint AJAX para edición inline de una fila de ClienteCC.
    Contrato de respuesta: {'ok': bool, 'saldo': str | None, 'error': str | None}
    """
    try:
        data = json.loads(request.body)
        cliente = get_object_or_404(ClienteCC, pk=data['id'])

        # Actualizar solo los campos enviados — no asumir cuáles vienen
        if 'vencido' in data:
            cliente.vencido = data['vencido']
        if 'balance_especial' in data:
            cliente.balance_especial = data['balance_especial']

        cliente.full_clean()  # ejecuta clean() del modelo antes de guardar
        cliente.save()

        return JsonResponse({'ok': True, 'saldo': str(cliente.saldo_total)})

    except ClienteCC.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Cliente no encontrado.'}, status=404)
    except (KeyError, ValueError) as e:
        return JsonResponse({'ok': False, 'error': f'Datos inválidos: {e}'}, status=400)
    except ValidationError as e:
        return JsonResponse({'ok': False, 'error': str(e.message)}, status=422)
    except Exception as e:
        logger.exception(f'Error inesperado en editar_fila: {e}')
        return JsonResponse({'ok': False, 'error': 'Error interno del servidor.'}, status=500)
```

### Reglas para vistas

- **Siempre** `@login_required` en vistas privadas — no confiar en que el template oculte el acceso.
- **Siempre** verificar rol en la vista, no solo en el template.
- Usar `get_object_or_404()` — nunca `.get()` directo.
- **Post/Redirect/Get (PRG)**: tras POST exitoso, siempre `redirect()`. Nunca `render()` tras un POST exitoso.
- Vistas AJAX: siempre `JsonResponse({'ok': bool, ...})` — respetar el contrato con el JS existente.
- Usar `messages.success/error/warning` para feedback — no variables de contexto ad-hoc.
- Llamar `full_clean()` antes de `save()` cuando no se usa un ModelForm (edición AJAX, importación).
- Usar `logger.exception()` dentro de bloques `except Exception` — captura el traceback completo.

### Decorador de control de roles

```python
# usuarios/decorators.py
import logging
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def requiere_rol(*roles):
    """
    Decorator que restringe el acceso a una vista según el rol del usuario.

    Uso:
        @requiere_rol('Administrador', 'Colaborador')
        def mi_vista(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.rol not in roles:
                logger.warning(
                    f'Acceso denegado: usuario {request.user.email} '
                    f'(rol={request.user.rol}) intentó acceder a vista '
                    f'restringida a {roles}.'
                )
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Función auxiliar interna (no decorator) — para usar dentro de una vista
def _verificar_rol(user, roles_permitidos):
    if user.rol not in roles_permitidos:
        raise PermissionDenied
```

---

## 5. Formularios Django

### ModelForm con validación personalizada

```python
from django import forms
from django.core.exceptions import ValidationError

from .models import ClienteCC


class ClienteCCForm(forms.ModelForm):
    class Meta:
        model = ClienteCC
        fields = ['nombre', 'vencido', 'balance_especial', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'vencido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'balance_especial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'nombre': 'Nombre del cliente',
            'vencido': 'Saldo vencido ($)',
            'balance_especial': 'Balance especial ($)',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise ValidationError('El nombre no puede estar vacío.')
        return nombre
```

### Form de carga de archivo Excel

```python
class NuevoMesForm(forms.Form):
    TAMANIO_MAXIMO_MB = 5
    EXTENSIONES_PERMITIDAS = ['.xlsx']

    archivo = forms.FileField(
        label='Archivo Excel (.xlsx)',
        help_text='Dos columnas: Nombre del cliente, Monto. Sin encabezado de la fila 1.'
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        nombre = archivo.name.lower()

        if not any(nombre.endswith(ext) for ext in self.EXTENSIONES_PERMITIDAS):
            raise ValidationError(
                f'El archivo debe ser de tipo: {", ".join(self.EXTENSIONES_PERMITIDAS)}'
            )

        limite = self.TAMANIO_MAXIMO_MB * 1024 * 1024
        if archivo.size > limite:
            raise ValidationError(
                f'El archivo no debe superar {self.TAMANIO_MAXIMO_MB}MB.'
            )

        return archivo
```

### Reglas para formularios

- Toda validación de entrada del usuario va en el formulario (`clean_campo()` o `clean()`), **nunca** en la vista.
- Usar `forms.ModelForm` cuando el formulario mapea directamente a un modelo.
- Las extensiones y límites de tamaño se definen como constantes de clase, no hardcodeados en `clean()`.
- Incluir siempre `{{ form.non_field_errors }}` y `{{ field.errors }}` en los templates.
- No duplicar validaciones que ya están en `model.clean()` — `form.save()` ejecuta ambas.
- No agregar `style=""` inline en los widgets — usar clases CSS del sistema de diseño.

---

## 6. URLs — namespaces y nombres semánticos

```python
# cuentas_corrientes/urls.py
from django.urls import path
from . import views

app_name = 'cuentas_corrientes'  # namespace obligatorio en todas las apps

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo-mes/', views.nuevo_mes, name='nuevo_mes'),
    path('exportar/', views.exportar, name='exportar'),
    path('importar/', views.importar, name='importar'),
    path('editar/', views.editar_fila, name='editar_fila'),  # endpoint AJAX
]
```

```python
# Estudio/urls.py — incluir con prefijo y namespace
from django.urls import path, include

urlpatterns = [
    path('cuentas-corrientes/', include('cuentas_corrientes.urls')),
    path('cotizaciones/', include('cotizaciones.urls')),
    path('', include('usuarios.urls')),
    path('admin/', admin.site.urls),
]
```

### Reglas para URLs

- **Siempre** definir `app_name` en cada `urls.py` de app.
- Referenciar URLs con `{% url 'app_name:nombre_vista' %}` en templates — nunca hardcodear rutas.
- En código Python: `reverse('app_name:nombre_vista')` o `redirect('app_name:nombre_vista')`.
- Nombres de URL en `snake_case`. Rutas en `kebab-case`.
- El endpoint AJAX de edición inline siempre en la misma app que los modelos que modifica.

---

## 7. Seguridad

### Tokens de activación y recuperación

```python
# usuarios/models.py
import uuid
from django.utils import timezone
from datetime import timedelta


class TokenActivacion(models.Model):
    EXPIRACION_HORAS = 24

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tokens_activacion'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    usado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Token de activación'
        verbose_name_plural = 'Tokens de activación'

    def __str__(self):
        return f'Token para {self.usuario.email}'

    @property
    def esta_vigente(self):
        """True si el token no fue usado y no expiró."""
        if self.usado:
            return False
        expiracion = self.fecha_creacion + timedelta(hours=self.EXPIRACION_HORAS)
        return timezone.now() < expiracion

    def consumir(self):
        """Invalidar el token inmediatamente tras ser usado — siempre de un solo uso."""
        self.usado = True
        self.save(update_fields=['usado'])
```

### Reglas de seguridad

- **Nunca** proteger rutas solo ocultando elementos en el template — siempre validar en la vista.
- Tokens de activación y recuperación: verificar expiración **y** que sean de un solo uso. Llamar `consumir()` inmediatamente al procesar.
- **CUIT argentino**: implementar validación de formato `XX-XXXXXXXX-X` **y** dígito verificador — no solo formato. Usar `validators.py`.
- Archivos subidos: validar extensión y tamaño en el form antes de procesar.
- Variables de configuración sensibles vienen de `python-decouple` (`.env`) — nunca hardcodear `SECRET_KEY`, credenciales, ni `DATABASE_URL`.
- CSRF: todos los forms POST incluyen `{% csrf_token %}`. Las peticiones AJAX incluyen `X-CSRFToken`.
- Usar `update_fields` en `.save()` cuando solo se actualiza un subconjunto de campos — evita race conditions y es más eficiente.
- Al importar archivos masivos (`/importar/`): verificar `is_staff` además del rol.

### CSRF en AJAX — implementación estándar

```javascript
// static/js/utils.js — función compartida
function getCsrfToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

// En cada archivo JS que haga fetch POST
async function postJson(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(data),
    });
    return response.json();
}
```

---

## 8. Services — lógica de negocio y APIs externas

### Service de lógica de negocio

```python
# cuentas_corrientes/services.py
import logging
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import ClienteCC, MesCC, ConfiguracionMeses

logger = logging.getLogger(__name__)


def procesar_nuevo_mes(archivo, periodo: date | None = None) -> dict:
    """
    Procesa la carga de un período de cuentas corrientes desde un archivo Excel.

    Maneja dos escenarios:
    - Primera carga del mes: rota la ventana de 5 períodos.
    - Carga adicional del mismo mes: acumula sobre el período existente.

    Args:
        archivo: Objeto InMemoryUploadedFile del form.
        periodo: Fecha del período a cargar. Por defecto, el mes actual.

    Returns:
        {'filas': int, 'nuevos': int, 'actualizados': int}

    Raises:
        ValidationError: Si el archivo tiene formato incorrecto o datos inválidos.
    """
    if periodo is None:
        hoy = date.today()
        periodo = date(hoy.year, hoy.month, 1)

    registros = _leer_excel_nuevo_mes(archivo)

    with transaction.atomic():
        es_primera_carga = not MesCC.objects.filter(periodo=periodo).exists()
        if es_primera_carga:
            _rotar_ventana_meses(periodo)

        nuevos, actualizados = _persistir_registros(registros, periodo)

    logger.info(
        f'Nuevo mes procesado: periodo={periodo}, '
        f'filas={len(registros)}, nuevos={nuevos}, actualizados={actualizados}'
    )

    return {'filas': len(registros), 'nuevos': nuevos, 'actualizados': actualizados}


def _leer_excel_nuevo_mes(archivo) -> list[dict]:
    """Parsea el Excel y retorna lista de {nombre, monto}. Privado al módulo."""
    import openpyxl
    try:
        wb = openpyxl.load_workbook(archivo, read_only=True, data_only=True)
        ws = wb.active
        registros = []
        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:
                continue
            nombre, monto = row[0], row[1]
            if not isinstance(monto, (int, float, Decimal)):
                raise ValidationError(
                    f'Fila {i}: el monto "{monto}" no es un número válido.'
                )
            registros.append({
                'nombre': str(nombre).strip(),
                'monto': Decimal(str(monto))
            })
        return registros
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Error al leer el archivo Excel: {e}')


def _rotar_ventana_meses(nuevo_periodo: date) -> None:
    """Acumula el mes más antiguo en vencido y lo elimina. Privado al módulo."""
    config = ConfiguracionMeses.objects.first()
    if not config:
        return
    # Lógica de rotación...


def _persistir_registros(registros: list[dict], periodo: date) -> tuple[int, int]:
    """Guarda o acumula los registros en DB. Retorna (nuevos, actualizados)."""
    nuevos = actualizados = 0
    for reg in registros:
        cliente, _ = ClienteCC.objects.get_or_create(nombre=reg['nombre'])
        mes, creado = MesCC.objects.get_or_create(
            cliente=cliente,
            periodo=periodo,
            defaults={'monto': Decimal('0')}
        )
        if creado:
            mes.monto = reg['monto']
            nuevos += 1
        else:
            mes.monto += reg['monto']  # carga adicional del mismo mes
            actualizados += 1
        mes.save()
    return nuevos, actualizados
```

### Service de API externa — patrón cotizaciones

```python
# cotizaciones/services.py
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TIMEOUT_SEGUNDOS = 5  # constante nombrada, no magic number


def obtener_cotizaciones_dolar() -> list[dict]:
    """
    Obtiene cotizaciones del dólar desde dolarapi.com.

    Retorna lista vacía ante cualquier error — nunca propaga excepciones al caller.
    El error queda registrado en el log para diagnóstico.
    """
    try:
        response = requests.get(
            'https://dolarapi.com/v1/dolares',
            timeout=TIMEOUT_SEGUNDOS
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        logger.error('Timeout al conectar con dolarapi.com — superó %ds.', TIMEOUT_SEGUNDOS)
        return []
    except requests.HTTPError as e:
        logger.error('Error HTTP al obtener cotizaciones: %s', e)
        return []
    except requests.RequestException as e:
        logger.error('Error de red al obtener cotizaciones: %s', e)
        return []
    except (ValueError, KeyError) as e:
        logger.error('Respuesta malformada de dolarapi.com: %s', e)
        return []
    except Exception as e:
        logger.exception('Error inesperado en obtener_cotizaciones_dolar: %s', e)
        return []
```

### Reglas para services

- **Siempre** `timeout` en llamadas con `requests`. Usar constante nombrada, no magic number.
- **Nunca** propagar excepciones de APIs externas — capturar, loguear, retornar vacío.
- Capturar excepciones específicas primero (`Timeout`, `HTTPError`) antes del genérico `RequestException`.
- Funciones privadas del módulo con prefijo `_` — no son parte de la interfaz pública del service.
- Usar `transaction.atomic()` en operaciones que modifican múltiples modelos — o todo, o nada.
- Docstring completo: qué hace, args, returns, raises.
- Los services retornan datos, nunca `HttpResponse` ni `JsonResponse`.

---

## 9. Procesamiento de Excel (openpyxl)

```python
# Lectura — siempre read_only=True para archivos grandes
import openpyxl
from decimal import Decimal
from django.core.exceptions import ValidationError


def leer_excel(archivo) -> list[dict]:
    try:
        wb = openpyxl.load_workbook(archivo, read_only=True, data_only=True)
        ws = wb.active
        registros = []
        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            nombre, monto = row[0], row[1]
            if not nombre:
                continue
            if not isinstance(monto, (int, float, Decimal)):
                raise ValidationError(f'Fila {i}: monto "{monto}" no es un número.')
            registros.append({'nombre': str(nombre).strip(), 'monto': Decimal(str(monto))})
        return registros
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Error al leer el archivo: {e}')


# Exportación — estilos en función separada
def exportar_clientes_a_excel(queryset) -> 'openpyxl.Workbook':
    """Genera Workbook a partir de un queryset de ClienteCC."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Clientes'
    _aplicar_estilos_encabezado(ws)
    for cliente in queryset:
        ws.append([cliente.nombre, float(cliente.vencido), float(cliente.saldo_total)])
    _ajustar_anchos_columnas(ws)
    return wb


def _aplicar_estilos_encabezado(ws) -> None:
    """Estilos de encabezado separados del contenido — función privada."""
    from openpyxl.styles import Font, PatternFill, Alignment
    encabezados = ['Nombre', 'Vencido', 'Saldo Total']
    for col, titulo in enumerate(encabezados, start=1):
        celda = ws.cell(row=1, column=col, value=titulo)
        celda.font = Font(bold=True, color='FFFFFF')
        celda.fill = PatternFill(fill_type='solid', fgColor='1F4E79')
        celda.alignment = Alignment(horizontal='center')


def _ajustar_anchos_columnas(ws) -> None:
    """Ajuste automático de ancho de columnas — función privada."""
    for col in ws.columns:
        max_len = max((len(str(c.value or '')) for c in col), default=0)
        ws.column_dimensions[col[0].column_letter].width = max_len + 4
```

### Reglas para Excel

- `read_only=True` al leer — evita cargar todo el archivo en memoria.
- Validar cada fila individualmente e incluir el número de fila en el mensaje de error.
- Estilos de exportación en funciones privadas `_` separadas del contenido.
- Usar `Decimal` para montos — nunca `float` al persistir en DB.
- Una sola librería: `openpyxl` tanto para lectura como escritura — no mezclar con `xlrd`, `xlwt` ni `pandas`.

---

## 10. Templates y Frontend

### Estructura de un template — plantilla de referencia

```html
{% extends 'base.html' %}
{% load static %}
{% load cc_tags %}

{% block title %}Cuentas Corrientes — Estudio Rivarossa{% endblock %}

{% block content %}
<div class="container-fluid px-4">

  <div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h3 mb-0">Cuentas Corrientes</h1>
    {% if request.user.rol == 'Administrador' %}
      <a href="{% url 'cuentas_corrientes:nuevo_mes' %}" class="btn btn-primary">
        <i class="bi bi-plus-lg me-1"></i>Nuevo mes
      </a>
    {% endif %}
  </div>

  {# Mensajes de Django — siempre incluir en vistas con acciones #}
  {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
      {{ message }}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    </div>
  {% endfor %}

  {# Contenido principal #}
  {% include 'cuentas_corrientes/partials/tabla_clientes.html' %}

</div>
{% endblock %}

{% block extra_js %}
  <script src="{% static 'js/cuentas_corrientes.js' %}"></script>
{% endblock %}
```

### Reglas para templates

- **Siempre** extender de `base.html` — nunca crear un HTML standalone.
- Usar variables CSS de `variables.css` para colores, espaciados y tipografía — no hardcodear valores en `style=""`.
- Revisar `components.css` antes de escribir CSS nuevo — el componente probablemente ya existe.
- No poner lógica de negocio en templates: nada de cálculos, no queries directos. Si el dato es calculado, usar `@property` o un `templatetag`.
- Extraer fragmentos repetidos a `{% include 'partials/nombre.html' %}`.
- Formularios: renderizar campo a campo con Bootstrap — no usar `{{ form.as_p }}` en producción.
- Paginación: usar `Paginator` de Django en la vista, renderizar controles en el template.
- **Nunca** hardcodear URLs — siempre `{% url 'app:nombre' %}`.
- Control de acceso en templates solo para **mostrar/ocultar UI** — la seguridad real va en la vista.

### Renderizar formulario campo a campo

```html
<form method="post" enctype="multipart/form-data" novalidate>
  {% csrf_token %}

  {% if form.non_field_errors %}
    <div class="alert alert-danger">
      {{ form.non_field_errors }}
    </div>
  {% endif %}

  <div class="mb-3">
    <label for="{{ form.archivo.id_for_label }}" class="form-label fw-semibold">
      {{ form.archivo.label }}
    </label>
    <input type="file"
           name="{{ form.archivo.html_name }}"
           id="{{ form.archivo.id_for_label }}"
           class="form-control {% if form.archivo.errors %}is-invalid{% endif %}"
           accept=".xlsx">
    {% if form.archivo.help_text %}
      <div class="form-text">{{ form.archivo.help_text }}</div>
    {% endif %}
    {% if form.archivo.errors %}
      <div class="invalid-feedback">{{ form.archivo.errors }}</div>
    {% endif %}
  </div>

  <button type="submit" class="btn btn-primary">
    <i class="bi bi-upload me-1"></i>Cargar
  </button>
</form>
```

### JavaScript — reglas y convenciones

```javascript
// static/js/cuentas_corrientes.js
// Cada página tiene su propio archivo JS.
// Una sola responsabilidad por archivo.

'use strict';

// Constantes al inicio del archivo
const URLS = {
    editarFila: document.getElementById('tabla-clientes')?.dataset.urlEditar,
};

// Inicialización en DOMContentLoaded — nunca en el scope global directo
document.addEventListener('DOMContentLoaded', () => {
    inicializarEdicionInline();
});

function inicializarEdicionInline() {
    document.querySelectorAll('[data-accion="editar-fila"]').forEach(btn => {
        btn.addEventListener('click', manejarEdicionFila);
    });
}

async function manejarEdicionFila(evento) {
    const fila = evento.target.closest('tr');
    const id = fila.dataset.clienteId;

    try {
        const resultado = await postJson(URLS.editarFila, {
            id,
            vencido: obtenerValorCelda(fila, 'vencido'),
        });

        if (resultado.ok) {
            actualizarSaldoEnFila(fila, resultado.saldo);
        } else {
            mostrarErrorEnFila(fila, resultado.error);
        }
    } catch (error) {
        console.error('Error al editar fila:', error);
        mostrarErrorEnFila(fila, 'Error de conexión.');
    }
}
```

**Reglas para JavaScript:**
- `'use strict'` al inicio de cada archivo.
- Constantes al inicio, lógica en funciones nombradas — nada en el scope global.
- `DOMContentLoaded` para inicializar — no ejecutar lógica al cargar el script.
- Funciones pequeñas con nombres que comunican intención.
- Siempre incluir `X-CSRFToken` en requests POST.
- Respetar el contrato JSON `{ok: bool, ...}` con el backend.
- No agregar librerías de gráficos adicionales — el proyecto usa **Chart.js** exclusivamente.
- Capturar errores de `fetch` con `try/catch` — nunca asumir que la request siempre funciona.

---

## 11. Admin de Django

```python
# cuentas_corrientes/admin.py
from django.contrib import admin
from .models import ClienteCC, MesCC, ConfiguracionMeses


@admin.register(ClienteCC)
class ClienteCCAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'vencido', 'balance_especial', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']
    ordering = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_per_page = 50


@admin.register(MesCC)
class MesCCAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'periodo', 'monto']
    list_filter = ['periodo']
    search_fields = ['cliente__nombre']
    ordering = ['cliente__nombre', 'periodo']
    list_per_page = 100


@admin.register(ConfiguracionMeses)
class ConfiguracionMesesAdmin(admin.ModelAdmin):
    list_display = ['__str__']
```

### Reglas para admin

- **Registrar todos los modelos** en `admin.py` desde el momento en que se crean — aunque la app aún no tenga vistas propias.
- Siempre definir `list_display`, `search_fields`, `ordering` y `list_per_page`.
- Campos de solo lectura (`auto_now`, `auto_now_add`) en `readonly_fields`.
- Usar `@admin.register(Modelo)` en lugar de `admin.site.register(Modelo, ClaseAdmin)`.

---

## 12. Logging — convenciones del proyecto

```python
# Al inicio de cada módulo que necesite logging
import logging
logger = logging.getLogger(__name__)  # __name__ siempre — da trazabilidad por módulo

# Niveles:
logger.debug('Detalle solo útil en desarrollo')        # Solo visible con DEBUG=True
logger.info('Evento relevante del negocio')            # Procesamiento exitoso, acciones importantes
logger.warning('Situación inusual, sistema sigue')     # Token expirado, API devolvió vacío
logger.error('Error recuperable — operación falló')    # API caída, archivo inválido
logger.exception('Error con traceback completo')       # Dentro de except Exception — siempre con traceback
```

### Reglas de logging

- **Nunca** usar `print()` — siempre `logger`.
- `logger.exception()` dentro de `except Exception` — captura el traceback completo automáticamente.
- Usar `%s` formatting en el logger, no f-strings — el logger evalúa el mensaje solo si se va a emitir.
- No loguear datos sensibles: contraseñas, tokens completos, números de documentos.
- En services de APIs externas: `logger.error()` ante cualquier falla de red o parseo.
- En vistas: `logger.warning()` para intentos de acceso no autorizado, `logger.exception()` para errores inesperados.

---

## 13. Migrations — reglas de integridad

```bash
# Flujo obligatorio ante cualquier cambio en models.py
python manage.py makemigrations nombre_app   # generar migración de la app específica
python manage.py migrate                     # aplicar
python manage.py showmigrations              # verificar estado
```

### Reglas para migrations

- Cada vez que se modifica `models.py`, generar y commitear la migración junto con el código.
- No modificar migraciones ya aplicadas en producción — crear una nueva.
- Nunca hacer `makemigrations --merge` sin entender qué está fusionando.
- Para renombrar campos o modelos: usar `RenameField`/`RenameModel` en la migración, no borrar y recrear.
- En campos con `default` que ya tienen datos en producción: siempre proveer un `default` válido en la migración o usar `RunPython`.

---

## 15. Checklist antes de dar una tarea por terminada

### Código nuevo o modificado

- [ ] ¿Cada función/método hace una sola cosa? ¿Su nombre comunica exactamente qué hace?
- [ ] ¿La lógica de negocio está en `services.py` o en el modelo, y no directamente en la vista?
- [ ] ¿Hay lógica duplicada que debería extraerse?
- [ ] ¿La app importa solo lo necesario de otras apps? ¿No hay acoplamiento innecesario?
- [ ] ¿Los `choices` y constantes están como atributos de clase, no como strings sueltos?
- [ ] ¿Los templates reutilizan `{% include %}` en lugar de duplicar HTML?
- [ ] ¿Las funciones superan 30 líneas? Si sí, ¿está justificado o hay que partir?

### Seguridad

- [ ] ¿La vista tiene `@login_required` y verificación de rol?
- [ ] ¿Los tokens se invalidan inmediatamente tras ser consumidos?
- [ ] ¿Las llamadas a APIs externas tienen `timeout` y capturan excepciones sin propagarlas?
- [ ] ¿Los formularios validan extensión y tamaño de archivos Excel?
- [ ] ¿Las peticiones AJAX incluyen `X-CSRFToken`?
- [ ] ¿No hay credenciales ni `SECRET_KEY` hardcodeadas?
- [ ] ¿El `.env` está en `.gitignore` y no se subió al repo?

### Modelos y DB

- [ ] ¿Los modelos nuevos tienen `__str__`, `class Meta`, `ordering`, `verbose_name`?
- [ ] ¿Se corrieron `makemigrations` + `migrate`?
- [ ] ¿Los modelos nuevos están registrados en `admin.py`?
- [ ] ¿Se usa `transaction.atomic()` en operaciones multi-modelo?
- [ ] ¿Se llama `full_clean()` antes de `save()` fuera de formularios?

### Frontend

- [ ] ¿Los templates extienden `base.html`?
- [ ] ¿Se usan variables CSS de `variables.css`? ¿No hay colores hardcodeados?
- [ ] ¿Las URLs en templates usan `{% url 'app:nombre' %}`?
- [ ] ¿Las vistas AJAX devuelven `JsonResponse({'ok': bool, ...})`?
- [ ] ¿El JS tiene `'use strict'` y lógica en `DOMContentLoaded`?

### Calidad

- [ ] ¿No hay `print()` — todo usa `logger`?
- [ ] ¿Los servicios de APIs externas usan `logger.error()`, no `print()`?
- [ ] ¿Las funciones de Excel usan `Decimal` para montos, no `float`?
- [ ] ¿Hay docstring en services, modelos y funciones complejas?
- [ ] ¿Se agregaron tests para la lógica nueva en `services.py` o `models.py`?