"""
Vistas a nivel de proyecto (no pertenecen a ninguna app específica).
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from usuarios.models import Usuario


def landing_view(request):
    """Landing page pública para usuarios no autenticados."""
    if request.user.is_authenticated:
        return home_view(request)
    return render(request, 'landing.html')


@login_required
def home_view(request):
    """Dashboard principal para usuarios autenticados."""
    usuario = request.user
    contexto = {
        'usuario': usuario,
        'empresas': usuario.empresas.filter(estado='activo'),
    }
    if usuario.rol == 'Administrador':
        contexto['total_usuarios'] = Usuario.objects.count()
        contexto['usuarios_pendientes'] = Usuario.objects.filter(estado='pendiente').count()
        contexto['usuarios_activos'] = Usuario.objects.filter(estado='verificado', is_active=True).count()
    return render(request, 'home.html', contexto)
