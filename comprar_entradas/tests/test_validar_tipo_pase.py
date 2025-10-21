import pytest

# Intentamos importar la función, si no existe vamos a manejarlo
try:
    from comprar_entradas.views import validar_tipo_pase
except ImportError:
    validar_tipo_pase = None

def test_validar_tipo_pase_valido():
    # Arrange
    pases_validos = ["VIP", "REGULAR"]

    if validar_tipo_pase is None:
        pytest.fail("La función 'validar_tipo_pase' no está implementada aún")

    # Act & Assert
    for pase in pases_validos:
        try:
            validar_tipo_pase(pase)
        except Exception as e:
            pytest.fail(f"No debería lanzar excepción para el pase '{pase}', pero lanzó: {e}")

def test_validar_tipo_pase_invalido():
    # Arrange
    pase_invalido = "SUPERVIP"  # tipo de pase no permitido

    if validar_tipo_pase is None:
        pytest.fail("La función 'validar_tipo_pase' no está implementada aún")

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        validar_tipo_pase(pase_invalido)

    # Verificamos que el mensaje contenga "inválido" o "válido"
    assert "inválido" in str(excinfo.value).lower() or "válido" in str(excinfo.value).lower()
