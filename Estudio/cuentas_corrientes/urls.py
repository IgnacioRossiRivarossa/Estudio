from django.urls import path
from . import views

app_name = 'cuentas_corrientes'

urlpatterns = [
    path('', views.lista_cuentas, name='lista'),
    path('editar/', views.editar_fila, name='editar_fila'),
    path('nuevo-mes/', views.nuevo_mes, name='nuevo_mes'),
    path('exportar/', views.exportar_excel, name='exportar'),
    path('importar/', views.importar_excel, name='importar'),
]
