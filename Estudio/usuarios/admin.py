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
from .utils import enviar_email_activacion_usuario

class EmpresaUsuarioInline(admin.TabularInline):
    model = Usuario.empresas.through
    extra = 1
    verbose_name = 'empresa asociada'
    verbose_name_plural = 'empresas asociadas'
    autocomplete_fields = ['empresa']

class UsuarioCreationForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido', 'rol', 'is_active', 'is_staff')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user

class UsuarioChangeForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = '__all__'


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
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
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            # Usuario nuevo: sin contraseña (se establecerá al activar)
            obj.set_unusable_password()
        super().save_model(request, obj, form, change)

    @admin.action(description='Enviar email de activación')
    def enviar_email_activacion(self, request, queryset):
        """Envía emails de activación de forma segura con manejo de errores."""
        enviados = 0
        errores = []
        
        for usuario in queryset:
            success, mensaje = enviar_email_activacion_usuario(usuario)
            
            if success:
                enviados += 1
            else:
                errores.append(f'{usuario.email}: {mensaje}')

        # Mostrar resultados
        if enviados > 0:
            self.message_user(
                request,
                f'✅ Se enviaron {enviados} email(s) de activación exitosamente.',
                level='success',
            )
        
        if errores:
            for error in errores:
                self.message_user(
                    request,
                    f'❌ {error}',
                    level='error',
                )

    @admin.action(description='Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        cantidad = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Se activaron {cantidad} usuario(s).',
        )

    @admin.action(description='Desactivar usuarios seleccionados')
    def desactivar_usuarios(self, request, queryset):
        cantidad = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Se desactivaron {cantidad} usuario(s).',
        )


@admin.register(TokenActivacion)
class TokenActivacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'creado_en', 'expira_en', 'esta_expirado']
    list_filter = ['tipo', 'creado_en']
    search_fields = ['usuario__email']
    readonly_fields = ['token', 'creado_en']

    def esta_expirado(self, obj):
        """Indicar si el token está expirado."""
        return obj.esta_expirado()

    esta_expirado.boolean = True
    esta_expirado.short_description = '¿Expirado?'
