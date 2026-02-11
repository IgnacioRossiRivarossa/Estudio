# Señales de la aplicación usuarios. Maneja el envío automático de email de activación cuando se crea un usuario nuevo desde el admin.
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Usuario, TokenActivacion

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Usuario)
def enviar_email_activacion(sender, instance, created, **kwargs):
    # Solo se envía si el usuario fue recién creado y está en estado 'pendiente'.
    # Genera un token de activación y envía el email con el link correspondiente.
    if created and instance.estado == 'pendiente' and not instance.is_superuser:
        try:
            # Crear o actualizar token de activación
            token_obj, _ = TokenActivacion.objects.update_or_create(
                usuario=instance,
                defaults={
                    'tipo': TokenActivacion.TipoToken.ACTIVACION,
                    'expira_en': timezone.now() + timedelta(hours=24),
                }
            )

            # Construir URL de activación
            # En producción, usar el dominio real
            if settings.DEBUG:
                dominio = 'localhost:8000'
            else:
                dominio = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
            protocolo = 'https' if not settings.DEBUG else 'http'
            url_activacion = f'{protocolo}://{dominio}/activate/{token_obj.token}/'

            # Renderizar template de email
            contexto = {
                'usuario': instance,
                'url_activacion': url_activacion,
                'expira_en': '24 horas',
            }
            html_message = render_to_string(
                'email/activacion_cuenta.html', contexto
            )
            plain_message = strip_tags(html_message)

            # Enviar email
            send_mail(
                subject='Bienvenido/a - Activa tu cuenta',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f'Email de activación enviado a {instance.email}')

        except Exception as e:
            logger.error(
                f'Error al enviar email de activación a {instance.email}: {str(e)}'
            )
