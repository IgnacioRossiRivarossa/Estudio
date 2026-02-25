from django.urls import path
from . import views

app_name = "cotizaciones"

urlpatterns = [
    path("", views.dashboard_economico_view, name="dashboard_economico"),
]
