from django.db import models
from decimal import Decimal

class ClienteCC(models.Model):
    nombre = models.CharField(
        'nombre',
        max_length=255,
        unique=True,
        help_text='Nombre del cliente de cuenta corriente.',
    )
    vencido = models.DecimalField(
        'vencido',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Acumulación de deudas antiguas.',
    )
    balance_especial = models.DecimalField(
        'balance/especial',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Deuda de tipo especial, editable manualmente.',
    )
    fecha_creacion = models.DateTimeField(
        'fecha de creación',
        auto_now_add=True,
    )
    activo = models.BooleanField(
        'activo',
        default=True,
        help_text='Indica si el cliente está activo. La baja solo se realiza desde el admin.',
    )

    class Meta:
        verbose_name = 'Cliente Cuenta Corriente'
        verbose_name_plural = 'Clientes Cuenta Corriente'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def saldo(self):
        periodos_activos = ConfiguracionMeses.objects.values_list('periodo', flat=True)
        suma_meses = self.meses.filter(
            periodo__in=periodos_activos
        ).aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')
        return self.vencido + self.balance_especial + suma_meses


class MesCC(models.Model):
    cliente = models.ForeignKey(
        ClienteCC,
        on_delete=models.CASCADE,
        related_name='meses',
        verbose_name='cliente',
    )
    periodo = models.DateField(
        'periodo',
        help_text='Mes del registro. Siempre guardar el día 1 del mes.',
    )
    monto = models.DecimalField(
        'monto',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
    )

    class Meta:
        verbose_name = 'Mes Cuenta Corriente'
        verbose_name_plural = 'Meses Cuenta Corriente'
        unique_together = ('cliente', 'periodo')
        ordering = ['periodo']

    def __str__(self):
        return f'{self.cliente.nombre} - {self.periodo.strftime("%b-%y")}'

class ConfiguracionMeses(models.Model):
    orden = models.PositiveSmallIntegerField(
        'orden',
        help_text='Orden del periodo (1 al 5). 1 = más antiguo, 5 = más reciente.',
    )
    periodo = models.DateField(
        'periodo',
        unique=True,
        help_text='Periodo activo. Siempre guardar el día 1 del mes.',
    )
    sumatoria_facturacion = models.DecimalField(
        'sumatoria facturación',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Sumatoria total de la columna al momento de crear el mes. Valor estático.',
    )

    class Meta:
        verbose_name = 'Configuración de Mes'
        verbose_name_plural = 'Configuración de Meses'
        ordering = ['orden']

    def __str__(self):
        return f'Mes-{self.orden}: {self.periodo.strftime("%b-%y")}'