import logging
import uuid
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from .models import TokenActivacion

logger = logging.getLogger(__name__)


def enviar_email_activacion_usuario(usuario):
    try:
        # Crear o actualizar token
        token_obj, _ = TokenActivacion.objects.update_or_create(
            usuario=usuario,
            defaults={
                'token': str(uuid.uuid4()),
                'tipo': TokenActivacion.TipoToken.ACTIVACION,
                'expira_en': timezone.now() + timedelta(hours=24),
            }
        )

        # Construir URL
        if settings.DEBUG:
            dominio = 'localhost:8000'
            protocolo = 'http'
        else:
            dominio = (
                settings.ALLOWED_HOSTS[0]
                if settings.ALLOWED_HOSTS
                else 'localhost'
            )
            protocolo = 'https'
        
        url_activacion = f'{protocolo}://{dominio}/activate/{token_obj.token}/'

        # Renderizar template
        contexto = {
            'usuario': usuario,
            'url_activacion': url_activacion,
            'expira_en': '24 horas',
        }
        html_message = render_to_string('email/activacion_cuenta.html', contexto)
        plain_message = strip_tags(html_message)

        # Intentar enviar email con timeout
        email = EmailMessage(
            subject='Bienvenido/a - Activa tu cuenta',
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[usuario.email],
        )
        email.content_subtype = 'html'
        email.body = html_message
        
        # Enviar con fail_silently=True para evitar bloqueos por timeout
        result = email.send(fail_silently=True)
        
        if result > 0:
            logger.info(f'✅ Email de activación enviado exitosamente a {usuario.email}')
            return True, f'Email enviado a {usuario.email}'
        else:
            logger.warning(f'⚠️ No se pudo enviar email a {usuario.email}. Verifica configuración SMTP.')
            return False, 'No se pudo enviar el email. Verifica las credenciales SMTP en las variables de entorno.'

    except Exception as e:
        error_msg = str(e)
        logger.error(
            f'Error al enviar email de activación a {usuario.email}: {error_msg}',
            exc_info=True
        )
        
        # Mensajes más amigables para errores comunes
        if 'timed out' in error_msg.lower() or 'timeout' in error_msg.lower():
            return False, f'Timeout al conectar con el servidor de email. Verifica la configuración SMTP.'
        elif 'authentication' in error_msg.lower() or 'credentials' in error_msg.lower():
            return False, f'Error de autenticación. Verifica EMAIL_HOST_USER y EMAIL_HOST_PASSWORD.'
        elif 'connection refused' in error_msg.lower():
            return False, f'Conexión rechazada. Verifica EMAIL_HOST y EMAIL_PORT.'
        else:
            return False, f'Error: {error_msg}'
