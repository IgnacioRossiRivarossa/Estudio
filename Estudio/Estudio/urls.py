from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from usuarios.views import home_view

# Personalización del sitio admin
admin.site.site_header = 'Estudio - Administración'
admin.site.site_title = 'Estudio Admin'
admin.site.index_title = 'Panel de Administración'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # URLs de usuarios (login, logout, activación, recuperación)
    path('', include('usuarios.urls')),

    # Dashboard (Home) - requiere login
    path('', home_view, name='home'),

    # robots.txt
    path(
        'robots.txt',
        RedirectView.as_view(url='/static/robots.txt', permanent=True),
    ),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Handlers para páginas de error personalizadas
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
