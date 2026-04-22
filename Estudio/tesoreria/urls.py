from django.urls import path
from . import views

app_name = 'tesoreria'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('exportar/', views.exportar_excel, name='exportar_excel'),
    path('caja-bancos/', views.caja_bancos, name='caja_bancos'),
    path('valores-a-depositar/', views.valores_a_depositar, name='valores_a_depositar'),
    path('inversiones/', views.inversiones, name='inversiones'),
    # API interna de actualización
    path('actualizar-precios/', views.actualizar_precios_titulos, name='actualizar_precios'),
    path('actualizar-semana/', views.actualizar_semana_titulos, name='actualizar_semana'),
    path('actualizar-semana-fci/', views.actualizar_semana_fci, name='actualizar_semana_fci'),
    path('actualizar-semana-caja/', views.actualizar_semana_caja, name='actualizar_semana_caja'),
    path('actualizar-semana-me/', views.actualizar_semana_me, name='actualizar_semana_me'),
    path('actualizar-semana-bancos/', views.actualizar_semana_bancos, name='actualizar_semana_bancos'),
    path('actualizar-semana-vad/', views.actualizar_semana_vad, name='actualizar_semana_vad'),
    # CRUD Caja
    path('caja/nueva/', views.caja_crear, name='caja_crear'),
    path('caja/<int:pk>/editar/', views.caja_editar, name='caja_editar'),
    # CRUD Banco
    path('banco/nuevo/', views.banco_crear, name='banco_crear'),
    path('banco/<int:pk>/editar/', views.banco_editar, name='banco_editar'),
    path('banco/<int:pk>/eliminar/', views.banco_eliminar, name='banco_eliminar'),
    # CRUD Moneda Extranjera
    path('moneda-extranjera/nueva/', views.moneda_extranjera_crear, name='moneda_extranjera_crear'),
    path('moneda-extranjera/<int:pk>/editar/', views.moneda_extranjera_editar, name='moneda_extranjera_editar'),
    path('moneda-extranjera/<int:pk>/eliminar/', views.moneda_extranjera_eliminar, name='moneda_extranjera_eliminar'),
    # CRUD Valores a Depositar
    path('vad/nuevo/', views.vad_crear, name='vad_crear'),
    path('vad/<int:pk>/editar/', views.vad_editar, name='vad_editar'),
    path('vad/<int:pk>/eliminar/', views.vad_eliminar, name='vad_eliminar'),
    # CRUD Plazo Fijo
    path('plazo-fijo/nuevo/', views.pf_crear, name='pf_crear'),
    path('plazo-fijo/<int:pk>/editar/', views.pf_editar, name='pf_editar'),
    path('plazo-fijo/<int:pk>/eliminar/', views.pf_eliminar, name='pf_eliminar'),
    # CRUD FCI
    path('fci/nuevo/', views.fci_crear, name='fci_crear'),
    path('fci/<int:pk>/editar/', views.fci_editar, name='fci_editar'),
    path('fci/<int:pk>/eliminar/', views.fci_eliminar, name='fci_eliminar'),
    # CRUD Títulos y ONs
    path('titulo/nuevo/', views.titulo_crear, name='titulo_crear'),
    path('titulo/<int:pk>/editar/', views.titulo_editar, name='titulo_editar'),
    path('titulo/<int:pk>/eliminar/', views.titulo_eliminar, name='titulo_eliminar'),
]