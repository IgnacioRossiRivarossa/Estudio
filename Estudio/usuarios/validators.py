import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MayusculaValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos una letra mayúscula.'),
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return _('La contraseña debe contener al menos una letra mayúscula.')


class NumeroValidator:
    def validate(self, password, user=None):
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _('La contraseña debe contener al menos un número.'),
                code='password_no_number',
            )

    def get_help_text(self):
        return _('La contraseña debe contener al menos un número.')
