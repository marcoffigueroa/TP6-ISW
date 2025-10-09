from django.test import TestCase
from comprar_entradas.views import validar_usuario_registrado

# Create your tests here.
def test_validar_usuario_registrado_con_usuario_valido():
    # Arrange
    usuario = {"id": 1, "email": "test@eco.com"}

    # Act & Assert
    # No debería lanzar ninguna excepción si el usuario es válido
    try:
        validar_usuario_registrado(usuario)
    except Exception as e:
        pytest.fail(f"No debería lanzar excepción, pero lanzó: {e}")