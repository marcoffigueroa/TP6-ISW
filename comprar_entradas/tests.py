from django.test import TestCase

# Create your tests here.
class ValidarUsuarioRegistradoTestCase(TestCase):
    def validar_usuario_registrado(usuario: dict):
        """
        Lanza ValueError si el usuario no está autenticado.
        """
        if not usuario or "id" not in usuario:
            raise ValueError("El usuario no está registrado.")