"""
Configuración del admin para la aplicación usuarios.

Incluye la configuración del modelo Usuario personalizado con
fieldsets organizados, acciones personalizadas e inline de empresas.
"""

import uuid
from datetime import timedelta

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import Usuario, TokenActivacion


class EmpresaUsuarioInline(admin.TabularInline):
    """Inline para gestionar empresas asociadas al usuario."""

    model = Usuario.empresas.through
    extra = 1
    verbose_name = 'empresa asociada'
    verbose_name_plural = 'empresas asociadas'
    autocomplete_fields = ['empresa']


class UsuarioCreationForm(forms.ModelForm):
    """Formulario para crear usuarios nuevos sin contraseña."""

    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido', 'rol', 'is_active', 'is_staff')

    def save(self, commit=True):
        """Guardar usuario con contraseña no usable."""
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    """Formulario para editar usuarios existentes."""

    class Meta:
        model = Usuario
        fields = '__all__'


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Configuración del admin para el modelo Usuario personalizado.

    Incluye listado, filtros, búsqueda, fieldsets organizados,
    inline de empresas y acciones personalizadas.
    """

    form = UsuarioChangeForm
    add_form = UsuarioCreationForm

    # Listado
    list_display = [
        'email',
        'nombre',
        'apellido',
        'rol',
        'estado',
        'is_active',
        'date_joined',
    ]
    list_filter = ['rol', 'estado', 'is_active', 'date_joined']
    search_fields = ['email', 'nombre', 'apellido']
    list_per_page = 25
    ordering = ['-date_joined']

    # Fieldsets para edición
    fieldsets = (
        ('Información Personal', {
            'fields': ('email', 'nombre', 'apellido'),
        }),
        ('Permisos y Rol', {
            'fields': ('rol', 'estado', 'is_active', 'is_staff', 'is_superuser'),
        }),
        ('Grupos y Permisos', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),
            'description': 'Permisos específicos y grupos del usuario.',
        }),
        ('Fechas importantes', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',),
        }),
    )

    # Fieldsets para creación (sin contraseña)
    add_fieldsets = (
        ('Información Personal', {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido'),
        }),
        ('Permisos y Rol', {
            'fields': ('rol', 'is_active', 'is_staff'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']
    filter_horizontal = ['groups', 'user_permissions']
    inlines = [EmpresaUsuarioInline]

    # Acciones personalizadas
    actions = [
        'enviar_email_activacion',
        'activar_usuarios',
        'desactivar_usuarios',
    ]

    def get_inline_instances(self, request, obj=None):
        """Solo mostrar inlines cuando se edita un usuario existente."""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        """
        Guardar modelo de usuario.

        Si es un usuario nuevo (creación), se establece contraseña no usable
        y se deja que la señal post_save envíe el email de activación.
        """
        if not change:
            # Usuario nuevo: sin contraseña (se establecerá al activar)
            obj.set_unusable_password()
        super().save_model(request, obj, form, change)

    @admin.action(description='Enviar email de activación')
    def enviar_email_activacion(self, request, queryset):
        """
        Acción para enviar email de activación a usuarios seleccionados.

        Genera un nuevo token y envía el email de activación.
        """
        enviados = 0
        for usuario in queryset:
            try:
                # Crear o actualizar token
                token_obj, _ = TokenActivacion.objects.update_or_create(
                    usuario=usuario,
                    defaults={
                        'token': str(uuid.uuid4()),
                        'tipo': TokenActivacion.TipoToken.ACTIVACION,
                        'expira_en': timezone.now() + timedelta(hours=24),
                    }
                )

                # Construir URL
                if settings.DEBUG:
                    dominio = 'localhost:8000'
                else:
                    dominio = (
                        settings.ALLOWED_HOSTS[0]
                        if settings.ALLOWED_HOSTS
                        else 'localhost'
                    )
                protocolo = 'https' if not settings.DEBUG else 'http'
                url_activacion = (
                    f'{protocolo}://{dominio}/activate/{token_obj.token}/'
                )

                # Enviar email
                contexto = {
                    'usuario': usuario,
                    'url_activacion': url_activacion,
                    'expira_en': '24 horas',
                }
                html_message = render_to_string(
                    'email/activacion_cuenta.html', contexto
                )
                plain_message = strip_tags(html_message)

                send_mail(
                    subject='Bienvenido/a - Activa tu cuenta',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                enviados += 1

            except Exception as e:
                self.message_user(
                    request,
                    f'Error al enviar email a {usuario.email}: {str(e)}',
                    level='error',
                )

        self.message_user(
            request,
            f'Se enviaron {enviados} email(s) de activación exitosamente.',
        )

    @admin.action(description='Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        """Activar usuarios seleccionados."""
        cantidad = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Se activaron {cantidad} usuario(s).',
        )

    @admin.action(description='Desactivar usuarios seleccionados')
    def desactivar_usuarios(self, request, queryset):
        """Desactivar usuarios seleccionados."""
        cantidad = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Se desactivaron {cantidad} usuario(s).',
        )


@admin.register(TokenActivacion)
class TokenActivacionAdmin(admin.ModelAdmin):
    """Configuración del admin para tokens de activación."""

    list_display = ['usuario', 'tipo', 'creado_en', 'expira_en', 'esta_expirado']
    list_filter = ['tipo', 'creado_en']
    search_fields = ['usuario__email']
    readonly_fields = ['token', 'creado_en']

    def esta_expirado(self, obj):
        """Indicar si el token está expirado."""
        return obj.esta_expirado()

    esta_expirado.boolean = True
    esta_expirado.short_description = '¿Expirado?'
