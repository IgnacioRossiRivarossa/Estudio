"""
Configuración del admin para la aplicación clientes.

Incluye la configuración del modelo Empresa con filtros,
búsqueda, inline de usuarios y validación de CUIT.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Empresa

Usuario = get_user_model()


class UsuarioEmpresaInline(admin.TabularInline):
    """Inline para mostrar usuarios asociados a una empresa."""

    model = Usuario.empresas.through
    extra = 0
    verbose_name = 'usuario asociado'
    verbose_name_plural = 'usuarios asociados'
    autocomplete_fields = ['usuario']


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Empresa."""

    list_display = [
        'nombre',
        'razon_social',
        'cuit',
        'email',
        'estado',
        'fecha_creacion',
    ]
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['nombre', 'razon_social', 'cuit', 'email']
    list_per_page = 25
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']

    fieldsets = (
        ('Información de la Empresa', {
            'fields': ('nombre', 'razon_social', 'cuit'),
        }),
        ('Contacto', {
            'fields': ('email', 'direccion'),
        }),
        ('Estado', {
            'fields': ('estado',),
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',),
        }),
    )

    inlines = [UsuarioEmpresaInline]
