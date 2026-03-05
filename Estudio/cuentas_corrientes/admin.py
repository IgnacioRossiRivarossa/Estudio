from django.contrib import admin
from .models import ClienteCC, MesCC, ConfiguracionMeses

@admin.action(description='Dar de baja clientes seleccionados (activo=False)')
def dar_de_baja(modeladmin, request, queryset):
    queryset.update(activo=False)

@admin.register(ClienteCC)
class ClienteCCAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'vencido', 'balance_especial', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    actions = [dar_de_baja]

@admin.register(MesCC)
class MesCCAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'periodo', 'monto')
    list_filter = ('periodo',)
    search_fields = ('cliente__nombre',)

@admin.register(ConfiguracionMeses)
class ConfiguracionMesesAdmin(admin.ModelAdmin):
    list_display = ('orden', 'periodo', 'sumatoria_facturacion')
    ordering = ('orden',)