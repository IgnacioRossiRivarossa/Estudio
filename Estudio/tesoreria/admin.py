from django.contrib import admin
from .models import Caja, Banco, MonedaExtranjera, ValorADepositar, ValorADepositarEmpresa, PlazoFijo, FCI, TituloON

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'saldo', 'fecha')
    list_filter = ('empresa', 'fecha')


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'saldo_cuenta_corriente', 'cheque_pendiente_acreditar',
                    'cheque_pendiente_debito', 'saldo_usd', 'fecha')
    list_filter = ('nombre', 'fecha')


@admin.register(MonedaExtranjera)
class MonedaExtranjeraAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'saldo_dolares', 'fecha')
    list_filter = ('empresa', 'fecha')


@admin.register(ValorADepositar)
class ValorADepositarAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'mes_vencimiento', 'anio_vencimiento', 'monto', 'fecha_carga')
    list_filter = ('empresa', 'mes_vencimiento', 'anio_vencimiento')


@admin.register(ValorADepositarEmpresa)
class ValorADepositarEmpresaAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'saldo_sem_ant')


@admin.register(PlazoFijo)
class PlazoFijoAdmin(admin.ModelAdmin):
    list_display = ('banco', 'monto_invertido', 'fecha_constitucion',
                    'fecha_vencimiento', 'interes', 'fecha_carga')
    list_filter = ('banco', 'fecha_carga')


@admin.register(FCI)
class FCIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'banco', 'cuotapartes', 'saldo', 'fecha')
    list_filter = ('banco', 'fecha')


@admin.register(TituloON)
class TituloONAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ticker', 'tipo', 'precio_manual', 'fecha',
                    'cuotapartes_actual', 'valor_cierre_pesos', 'valor_cierre_usd',
                    'saldo_pesos_actual', 'saldo_usd_actual')
    list_filter = ('tipo', 'precio_manual', 'fecha')

    # Campos que siempre son readonly (IOL los calcula automáticamente para
    # títulos normales). Para precio_manual=True se quitan del readonly en
    # get_readonly_fields para que el admin pueda editarlos a mano.
    _CAMPOS_IOL = (
        'valor_cierre_pesos', 'valor_cierre_usd',
        'saldo_pesos_actual', 'saldo_usd_actual',
    )
    _CAMPOS_SEM_ANT = (
        'cuotapartes_sem_ant', 'saldo_pesos_sem_ant', 'saldo_usd_sem_ant',
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.precio_manual:
            # Precio manual: solo sem_ant es readonly (no tiene sentido editarla aquí)
            return self._CAMPOS_SEM_ANT
        # Precio vía IOL: todos los calculados son readonly
        return self._CAMPOS_IOL + self._CAMPOS_SEM_ANT

    fieldsets = (
        ('Identificación', {
            'fields': ('nombre', 'ticker', 'tipo', 'fecha'),
        }),
        ('Configuración de precio', {
            'fields': ('precio_manual',),
            'description': (
                'Activar si este título NO cotiza en IOL. '
                'Al activarlo podrá ingresar el precio y los saldos manualmente.'
            ),
        }),
        ('Tenencia actual', {
            'fields': ('cuotapartes_actual',),
        }),
        ('Precios de cierre', {
            'fields': ('valor_cierre_pesos', 'valor_cierre_usd'),
        }),
        ('Saldos actuales', {
            'fields': ('saldo_pesos_actual', 'saldo_usd_actual'),
        }),
        ('Semana anterior', {
            'fields': ('cuotapartes_sem_ant', 'saldo_pesos_sem_ant', 'saldo_usd_sem_ant'),
            'classes': ('collapse',),
        }),
    )
