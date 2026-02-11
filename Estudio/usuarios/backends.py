"""
Backend de autenticación personalizado para el modelo Usuario.

Permite autenticar usuarios usando email en lugar de username.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class EmailBackend(ModelBackend):
    """
    Backend de autenticación que usa email como identificador.

    Valida que el usuario esté verificado antes de permitir el login.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autenticar usuario por email y contraseña.

        Args:
            request: Objeto HttpRequest.
            username: Email del usuario (Django usa 'username' como parámetro).
            password: Contraseña del usuario.

        Returns:
            Instancia de Usuario si la autenticación es exitosa, None en caso contrario.
        """
        email = username or kwargs.get('email')
        if email is None or password is None:
            return None

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            # Ejecutar el hasher de contraseña para prevenir ataques de timing
            Usuario().set_password(password)
            return None

        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None

    def get_user(self, user_id):
        """
        Obtener usuario por su ID.

        Args:
            user_id: ID del usuario.

        Returns:
            Instancia de Usuario o None.
        """
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
