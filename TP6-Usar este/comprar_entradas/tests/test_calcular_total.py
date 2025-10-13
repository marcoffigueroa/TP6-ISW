# tests/unit/test_calcular_total.py
import pytest

def test_calcular_total_suma_correctamente_las_lineas():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import calcular_total
    except ImportError:
        pytest.fail("La función 'calcular_total' no está definida o no se puede importar")

    # Arrange
    borrador = {
        "lineas": [
            {"visitante": {"nombre": "Ana"}, "precio": {"monto": 10000, "moneda": "ARS"}},
            {"visitante": {"nombre": "Luis"}, "precio": {"monto": 15000, "moneda": "ARS"}},
            {"visitante": {"nombre": "Marta"}, "precio": {"monto": 8000, "moneda": "ARS"}},
        ]
    }

    # motor_precios no se usa acá, pero dejamos un placeholder
    motor_precios_mock = lambda visitante, tipo_pase=None: visitante.get("precio", {}).get("monto", 0)

    # Act
    total = calcular_total(borrador, motor_precios_mock)

    # Assert
    total_esperado = 10000 + 15000 + 8000
    assert isinstance(total, (int, float)), "El total debería ser numérico"
    assert total == total_esperado, f"El total calculado debería ser {total_esperado}, pero fue {total}"

def test_calcular_total_con_lista_vacia_devuelve_cero():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import calcular_total
    except ImportError:
        pytest.fail("La función 'calcular_total' no está definida o no se puede importar")

    # Arrange: borrador sin líneas
    borrador = {"lineas": []}
    motor_precios_mock = lambda visitante, tipo_pase=None: 0

    # Act
    total = calcular_total(borrador, motor_precios_mock)

    # Assert
    assert total == 0, f"El total debería ser 0 cuando no hay líneas, pero fue {total}"