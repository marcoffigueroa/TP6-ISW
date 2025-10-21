from comprar_entradas.views import validar_cantidad_entradas
import pytest

def test_validar_cantidad_entradas_valida():
    cantidad = 0  # caso inválido

    resultado = validar_cantidad_entradas(cantidad)

    assert resultado is True  # fallará si la función devuelve False o None

def test_validar_cantidad_entradas_mayor_a_limite():
    cantidad = 12  # supera el límite permitido (10)

    # Esperamos que la función lance un ValueError
    with pytest.raises(ValueError) as excinfo:
        validar_cantidad_entradas(cantidad)

    # Verificamos que el mensaje de error sea el esperado
    assert "máximo" in str(excinfo.value).lower() or "limite" in str(excinfo.value).lower()

