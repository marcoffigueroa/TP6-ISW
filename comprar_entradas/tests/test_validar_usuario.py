import pytest
from comprar_entradas.views import validar_usuario_registrado
from comprar_entradas.constants import USUARIOS_REGISTRADOS

# Create your tests here.
def test_validar_usuario_registrado_con_usuario_valido():
    # Arrange
    # Usar un usuario de la lista de USUARIOS_REGISTRADOS
    usuario = {"id": 1, "email": "marco.figueroa@example.com"}

    # Act & Assert
    # No debería lanzar ninguna excepción si el usuario es válido
    try:
        validar_usuario_registrado(usuario)
    except Exception as e:
        pytest.fail(f"No debería lanzar excepción, pero lanzó: {e}")

def test_validar_usuario_registrado_con_usuario_none():
    # Arrange
    usuario = None  # usuario no autenticado o inexistente

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        validar_usuario_registrado(usuario)

    # Assert - mensaje esperado
    assert "usuario" in str(excinfo.value).lower() or "registrado" in str(excinfo.value).lower()

def test_validar_usuario_en_lista_registrados():
    # Arrange
    # Tomamos un usuario de la lista de USUARIOS_REGISTRADOS
    usuario_lista = USUARIOS_REGISTRADOS[0]  # Tomas Vergara
    usuario = {
        "id": 1, 
        "email": usuario_lista['mail'],
        "nombre": usuario_lista['nombre']
    }

    # Act & Assert
    # No debería lanzar ninguna excepción si el usuario está en la lista
    try:
        validar_usuario_registrado(usuario)
    except Exception as e:
        pytest.fail(f"No debería lanzar excepción para usuario registrado, pero lanzó: {e}")

def test_validar_usuario_no_en_lista_registrados():
    # Arrange
    # Usuario válido pero no está en la lista de USUARIOS_REGISTRADOS
    usuario = {
        "id": 999,
        "email": "usuario.noregistrado@example.com",
        "nombre": "Usuario No Registrado"
    }

    # Act & Assert
    # Debería lanzar excepción si el usuario no está en la lista
    with pytest.raises(ValueError) as excinfo:
        validar_usuario_registrado(usuario)
    
    # Assert - mensaje esperado
    assert "no está en la lista de usuarios registrados" in str(excinfo.value).lower() or "no registrado" in str(excinfo.value).lower()