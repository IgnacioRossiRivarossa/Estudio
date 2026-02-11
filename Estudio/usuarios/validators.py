"""
Validadores de contraseña personalizados.

Implementan las políticas de contraseña requeridas:
- Mínimo una letra mayúscula
- Mínimo un número
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MayusculaValidator:
    """Validador que requiere al menos una letra mayúscula en la contraseña."""

    def validate(self, password, user=None):
        """Validar que la contraseña contenga al menos una mayúscula."""
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos una letra mayúscula.'),
                code='password_no_uppercase',
            )

    def get_help_text(self):
        """Texto de ayuda para el validador."""
        return _('La contraseña debe contener al menos una letra mayúscula.')


class NumeroValidator:
    """Validador que requiere al menos un número en la contraseña."""

    def validate(self, password, user=None):
        """Validar que la contraseña contenga al menos un número."""
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos un número.'),
                code='password_no_number',
            )

    def get_help_text(self):
        """Texto de ayuda para el validador."""
        return _('La contraseña debe contener al menos un número.')
