from datetime import date
from django.db import models

EMPRESA_CHOICES = [
    ('L1', 'L1'),
    ('L2', 'L2'),
]

class Caja(models.Model):
    fecha = models.DateField(default=date.today)
    empresa = models.CharField(max_length=2, choices=EMPRESA_CHOICES)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_sem_ant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['empresa']

    def __str__(self):
        return f"Caja {self.empresa} - {self.fecha}"

class Banco(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField(default=date.today)
    saldo_cuenta_corriente = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cheque_pendiente_acreditar = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, blank=True, null=True
    )
    cheque_pendiente_debito = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, blank=True, null=True
    )
    saldo_usd = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, blank=True, null=True
    )
    saldo_sem_ant_pesos = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    saldo_usd_sem_ant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    class Meta:
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.fecha}"

class MonedaExtranjera(models.Model):
    fecha = models.DateField(default=date.today)
    empresa = models.CharField(max_length=2, choices=EMPRESA_CHOICES)
    saldo_dolares = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_dolares_sem_ant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Moneda Extranjera'
        verbose_name_plural = 'Monedas Extranjeras'
        ordering = ['empresa']

    def __str__(self):
        return f"ME {self.empresa} - {self.fecha}"

class ValorADepositarEmpresa(models.Model):
    empresa = models.CharField(max_length=2, choices=EMPRESA_CHOICES, unique=True)
    saldo_sem_ant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'VAD Empresa Sem. Ant.'
        verbose_name_plural = 'VAD Empresas Sem. Ant.'

    def __str__(self):
        return f"VAD Empresa {self.empresa}"


class ValorADepositar(models.Model):
    fecha_carga = models.DateField(default=date.today)
    empresa = models.CharField(max_length=2, choices=EMPRESA_CHOICES)
    mes_vencimiento = models.CharField(max_length=20)
    anio_vencimiento = models.IntegerField()
    monto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    class Meta:
        verbose_name = 'Valor a Depositar'
        verbose_name_plural = 'Valores a Depositar'
        ordering = ['anio_vencimiento', 'mes_vencimiento']

    def __str__(self):
        return f"VAD {self.empresa} - {self.mes_vencimiento} {self.anio_vencimiento}"

class PlazoFijo(models.Model):
    banco = models.CharField(max_length=100)
    monto_invertido = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    fecha_constitucion = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    interes = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    fecha_carga = models.DateField(default=date.today)
    class Meta:
        verbose_name = 'Plazo Fijo'
        verbose_name_plural = 'Plazos Fijos'
        ordering = ['banco']

    def __str__(self):
        return f"PF {self.banco} - {self.monto_invertido}"

class FCI(models.Model):
    nombre = models.CharField(max_length=200)
    banco = models.CharField(max_length=100)
    fecha = models.DateField(default=date.today)
    cuotapartes_sem_ant = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    saldo_sem_ant = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    cuotapartes = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    saldo = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    class Meta:
        verbose_name = 'FCI'
        verbose_name_plural = 'FCIs'
        ordering = ['nombre']

    def __str__(self):
        return f"FCI {self.nombre} ({self.banco})"

TIPO_TITULO_CHOICES = [
    ('ON', 'Obligación Negociable'),
    ('Bono', 'Bono'),
]

class TituloON(models.Model):
    nombre = models.CharField(max_length=200)
    ticker = models.CharField(max_length=20)
    tipo = models.CharField(max_length=10, choices=TIPO_TITULO_CHOICES, default='ON')
    fecha = models.DateField(default=date.today)
    cuotapartes_sem_ant = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    saldo_pesos_sem_ant = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    saldo_usd_sem_ant = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    cuotapartes_actual = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    saldo_pesos_actual = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    saldo_usd_actual = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    valor_cierre_pesos = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    valor_cierre_usd = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    class Meta:
        verbose_name = 'Título / ON'
        verbose_name_plural = 'Títulos / ONs'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.ticker})"

    @property
    def es_panama(self):
        return 'panama' in self.nombre.lower()