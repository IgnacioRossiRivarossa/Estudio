from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ValorADepositar, ValorADepositarEmpresa


@receiver(post_delete, sender=ValorADepositar)
def limpiar_snapshot_empresa(sender, instance, **kwargs):
    """
    Después de eliminar un ValorADepositar, verifica si quedan registros
    para esa empresa. Si no quedan, elimina el snapshot de semana anterior
    para evitar que el dashboard muestre datos huérfanos.
    """
    if not ValorADepositar.objects.filter(empresa=instance.empresa).exists():
        ValorADepositarEmpresa.objects.filter(empresa=instance.empresa).delete()
