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
    list_display = ('nombre', 'ticker', 'fecha', 'cuotapartes_actual',
                    'valor_cierre_pesos', 'valor_cierre_usd',
                    'saldo_pesos_actual', 'saldo_usd_actual')
    list_filter = ('fecha',)
    readonly_fields = (
        'valor_cierre_pesos', 'valor_cierre_usd',
        'saldo_pesos_actual', 'saldo_usd_actual',
        'cuotapartes_sem_ant', 'saldo_pesos_sem_ant', 'saldo_usd_sem_ant',
    )
