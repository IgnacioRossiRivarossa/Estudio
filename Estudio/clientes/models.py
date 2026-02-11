"""
Modelos de la aplicación clientes.

Incluye el modelo Empresa para la gestión de clientes empresariales.
"""

import re

from django.core.exceptions import ValidationError
from django.db import models


def validar_cuit(value):
    """
    Validar formato de CUIT argentino.

    El CUIT debe:
    - Tener exactamente 11 dígitos numéricos.
    - Pasar la validación del dígito verificador.

    Args:
        value: String con el CUIT a validar.

    Raises:
        ValidationError: Si el CUIT no tiene formato válido.
    """
    # Eliminar guiones si los tiene
    cuit_limpio = re.sub(r'[-]', '', value)

    if not cuit_limpio.isdigit():
        raise ValidationError('El CUIT debe contener solo números.')

    if len(cuit_limpio) != 11:
        raise ValidationError('El CUIT debe tener exactamente 11 dígitos.')

    # Validación del dígito verificador
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(cuit_limpio[i]) * base[i] for i in range(10))
    resto = 11 - (total % 11)

    if resto == 11:
        digito_verificador = 0
    elif resto == 10:
        digito_verificador = 9
    else:
        digito_verificador = resto

    if int(cuit_limpio[10]) != digito_verificador:
        raise ValidationError('El CUIT ingresado no es válido.')


class Empresa(models.Model):
    """
    Modelo para representar una empresa cliente.

    Almacena los datos de las empresas asociadas a los usuarios
    del sistema.
    """

    class Estado(models.TextChoices):
        """Opciones de estado de la empresa."""
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'

    nombre = models.CharField(
        'nombre',
        max_length=200,
        help_text='Nombre comercial de la empresa.',
    )
    razon_social = models.CharField(
        'razón social',
        max_length=200,
        help_text='Razón social registrada.',
    )
    cuit = models.CharField(
        'CUIT',
        max_length=11,
        unique=True,
        validators=[validar_cuit],
        help_text='CUIT sin guiones (11 dígitos).',
        error_messages={
            'unique': 'Ya existe una empresa con este CUIT.',
        },
    )
    direccion = models.TextField(
        'dirección',
        help_text='Dirección fiscal de la empresa.',
    )
    email = models.EmailField(
        'correo electrónico',
        help_text='Email de contacto de la empresa.',
    )
    estado = models.CharField(
        'estado',
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    fecha_creacion = models.DateTimeField(
        'fecha de creación',
        auto_now_add=True,
    )
    fecha_modificacion = models.DateTimeField(
        'fecha de modificación',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['cuit'], name='idx_empresa_cuit'),
            models.Index(fields=['estado'], name='idx_empresa_estado'),
            models.Index(fields=['nombre'], name='idx_empresa_nombre'),
        ]

    def __str__(self):
        """Representación en texto de la empresa."""
        return self.nombre

    def clean(self):
        """Validar datos de la empresa antes de guardar."""
        super().clean()
        # Limpiar CUIT de guiones antes de validar
        if self.cuit:
            self.cuit = re.sub(r'[-]', '', self.cuit)
