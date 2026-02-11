# Incluye vistas para login, logout, activación de cuenta, recuperación de contraseña y dashboard principal.
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .forms import EstablecerPasswordForm, LoginForm, SolicitarRecuperacionForm
from .models import TokenActivacion, Usuario

logger = logging.getLogger(__name__)


def login_view(request):
    # Vista de inicio de sesión, Muestra formulario de login y autentica usuario por email y contraseña. Redirige al dashboard si la autenticación es exitosa.
    # Si el usuario ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']

            # Configurar duración de sesión según "Recordarme"
            if not form.cleaned_data.get('recordarme'):
                request.session.set_expiry(0)  # Cierra al cerrar navegador
            else:
                request.session.set_expiry(86400 * 30)  # 30 días

            login(request, user)
            messages.success(request, f'¡Bienvenido/a, {user.get_full_name()}!')

            # Redirigir a URL solicitada o al home
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    # Vista de cierre de sesión. Cierra la sesión del usuario y redirige al login.
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


def activate_view(request, token):
    # Vista de activación de cuenta. Valida el token de activación y muestra formulario para establecer la contraseña inicial del usuario.
    try:
        token_obj = TokenActivacion.objects.get(
            token=token,
            tipo=TokenActivacion.TipoToken.ACTIVACION,
        )
    except TokenActivacion.DoesNotExist:
        messages.error(
            request,
            'El enlace de activación no es válido. '
            'Contacta al administrador para solicitar uno nuevo.'
        )
        return redirect('login')

    # Verificar si el token ha expirado
    if token_obj.esta_expirado():
        messages.error(
            request,
            'El enlace de activación ha expirado. '
            'Contacta al administrador para solicitar uno nuevo.'
        )
        return redirect('login')

    usuario = token_obj.usuario

    # Si el usuario ya está verificado
    if usuario.estado == 'verificado':
        messages.info(request, 'Tu cuenta ya ha sido activada. Inicia sesión.')
        return redirect('login')

    if request.method == 'POST':
        form = EstablecerPasswordForm(request.POST)
        if form.is_valid():
            # Establecer contraseña y activar usuario
            usuario.set_password(form.cleaned_data['password1'])
            usuario.estado = 'verificado'
            usuario.save(update_fields=['password', 'estado'])

            # Eliminar token usado
            token_obj.delete()

            messages.success(
                request,
                '¡Tu cuenta ha sido activada exitosamente! '
                'Ya puedes iniciar sesión.'
            )
            return redirect('login')
    else:
        form = EstablecerPasswordForm()

    return render(request, 'usuarios/activate.html', {
        'form': form,
        'usuario': usuario,
    })


def password_reset_view(request):
    # Vista para solicitar recuperación de contraseña. Envía un email con un link para restablecer la contraseña si el email existe en el sistema.
    if request.method == 'POST':
        form = SolicitarRecuperacionForm(request.POST)
        if form.is_valid():
            usuario = form.usuario

            if usuario:
                try:
                    # Crear o actualizar token de recuperación
                    token_obj, _ = TokenActivacion.objects.update_or_create(
                        usuario=usuario,
                        defaults={
                            'tipo': TokenActivacion.TipoToken.RECUPERACION,
                            'expira_en': timezone.now() + timedelta(hours=24),
                        }
                    )
                    # Regenerar token
                    import uuid
                    token_obj.token = str(uuid.uuid4())
                    token_obj.save(update_fields=['token'])

                    # Construir URL de recuperación
                    if settings.DEBUG:
                        dominio = 'localhost:8000'
                    else:
                        dominio = (
                            settings.ALLOWED_HOSTS[0]
                            if settings.ALLOWED_HOSTS
                            else 'localhost'
                        )
                    protocolo = 'https' if not settings.DEBUG else 'http'
                    url_recuperacion = (
                        f'{protocolo}://{dominio}'
                        f'/password-reset-confirm/{token_obj.token}/'
                    )

                    # Enviar email
                    contexto = {
                        'usuario': usuario,
                        'url_recuperacion': url_recuperacion,
                        'expira_en': '24 horas',
                    }
                    html_message = render_to_string(
                        'email/recuperacion_password.html', contexto
                    )
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject='Recuperación de contraseña',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[usuario.email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    logger.info(
                        f'Email de recuperación enviado a {usuario.email}'
                    )

                except Exception as e:
                    logger.error(
                        f'Error al enviar email de recuperación: {str(e)}'
                    )

            # Siempre mostrar mensaje de éxito (no revelar si email existe)
            messages.success(
                request,
                'Si el email está registrado, recibirás un enlace '
                'para restablecer tu contraseña.'
            )
            return redirect('login')
    else:
        form = SolicitarRecuperacionForm()

    return render(request, 'usuarios/password_reset.html', {'form': form})


def password_reset_confirm_view(request, token):
    # Vista para confirmar y establecer nueva contraseña.Valida el token de recuperación y permite al usuario establecer una nueva contraseña.
    try:
        token_obj = TokenActivacion.objects.get(
            token=token,
            tipo=TokenActivacion.TipoToken.RECUPERACION,
        )
    except TokenActivacion.DoesNotExist:
        messages.error(
            request,
            'El enlace de recuperación no es válido o ya ha sido utilizado.'
        )
        return redirect('login')

    # Verificar si el token ha expirado
    if token_obj.esta_expirado():
        messages.error(
            request,
            'El enlace de recuperación ha expirado. Solicita uno nuevo.'
        )
        return redirect('password_reset')

    usuario = token_obj.usuario

    if request.method == 'POST':
        form = EstablecerPasswordForm(request.POST)
        if form.is_valid():
            # Establecer nueva contraseña
            usuario.set_password(form.cleaned_data['password1'])
            usuario.save(update_fields=['password'])

            # Eliminar token usado
            token_obj.delete()

            messages.success(
                request,
                'Tu contraseña ha sido restablecida exitosamente. '
                'Ya puedes iniciar sesión con tu nueva contraseña.'
            )
            return redirect('login')
    else:
        form = EstablecerPasswordForm()

    return render(request, 'usuarios/password_reset_confirm.html', {
        'form': form,
        'usuario': usuario,
    })


@login_required
def home_view(request):
    # Vista del dashboard principal. Requiere autenticación. Muestra información diferente según el rol del usuario.
    usuario = request.user

    contexto = {
        'usuario': usuario,
        'empresas': usuario.empresas.filter(estado='activo'),
    }

    # Información adicional según rol
    if usuario.rol == 'Administrador':
        contexto['total_usuarios'] = Usuario.objects.count()
        contexto['usuarios_pendientes'] = Usuario.objects.filter(
            estado='pendiente'
        ).count()
        contexto['usuarios_activos'] = Usuario.objects.filter(
            estado='verificado', is_active=True
        ).count()

    return render(request, 'home.html', contexto)
