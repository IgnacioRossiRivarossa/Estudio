from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<str:token>/', views.activate_view, name='activate'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path(
        'password-reset-confirm/<str:token>/',
        views.password_reset_confirm_view,
        name='password_reset_confirm',
    ),
]
