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

def test_validar_usuario_registrado_con_usuario_none():
    # Arrange
    usuario = None  # usuario no autenticado o inexistente

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        validar_usuario_registrado(usuario)

    # Assert - mensaje esperado
    assert "usuario" in str(excinfo.value).lower()