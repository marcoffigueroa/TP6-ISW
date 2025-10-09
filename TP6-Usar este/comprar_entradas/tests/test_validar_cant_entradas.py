from comprar_entradas.views import validar_cantidad_entradas
import pytest

def test_validar_cantidad_entradas_valida():
    cantidad = 0  # caso inválido

    resultado = validar_cantidad_entradas(cantidad)

    assert resultado is True  # fallará si la función devuelve False o None
