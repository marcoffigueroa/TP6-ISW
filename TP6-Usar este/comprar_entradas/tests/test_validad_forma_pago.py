import pytest

# Intentamos importar la función, si no existe vamos a manejarlo
try:
    from comprar_entradas.views import validar_forma_pago
except ImportError:
    validar_forma_pago = None

def test_validar_forma_pago_valida():
    # Arrange
    formas_validas = ["EFECTIVO", "TARJETA"]

    if validar_forma_pago is None:
        # La función no está implementada → marcamos FAILED
        pytest.fail("La función 'validar_forma_pago' no está implementada aún")

    # Act & Assert
    for forma in formas_validas:
        try:
            validar_forma_pago(forma)
        except Exception as e:
            pytest.fail(f"No debería lanzar excepción para '{forma}', pero lanzó: {e}")

def test_validar_forma_pago_invalida():
    # Arrange
    forma_invalida = "BITCOIN"  # forma de pago no permitida

    if validar_forma_pago is None:
        pytest.fail("La función 'validar_forma_pago' no está implementada aún")

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        validar_forma_pago(forma_invalida)

    # Verificamos que el mensaje contenga "inválida" o "válida"
    assert "inválida" in str(excinfo.value).lower() or "válida" in str(excinfo.value).lower()