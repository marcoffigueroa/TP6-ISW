# tests/unit/test_construir_borrador_orden.py
import pytest
from datetime import date

def test_construir_borrador_orden_correcto():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import construir_borrador_orden
    except ImportError:
        pytest.fail("La función 'construir_borrador_orden' no está definida o no se puede importar")

    # Arrange
    usuario = {"id": 1, "nombre": "Marco"}
    fecha_visita = date.today()
    visitantes = [
        {"nombre": "Ana", "edad": 25},
        {"nombre": "Luis", "edad": 30},
    ]
    tipo_pase = "REGULAR"
    forma_pago = "TARJETA"

    # motor_precios mockeado simple
    def motor_precios_mock(visitante, tipo_pase):
        return {"monto": 10000, "moneda": "ARS"}

    # Act
    borrador = construir_borrador_orden(
        usuario=usuario,
        fecha_visita=fecha_visita,
        visitantes=visitantes,
        tipo_pase=tipo_pase,
        forma_pago=forma_pago,
        motor_precios=motor_precios_mock
    )

    # Assert
    assert isinstance(borrador, dict), "El resultado debe ser un diccionario"
    assert borrador.get("usuario") == usuario
    assert borrador.get("fecha_visita") == fecha_visita
    assert borrador.get("forma_pago") == forma_pago
    assert borrador.get("tipo_pase") == tipo_pase
    assert "lineas" in borrador and len(borrador["lineas"]) == len(visitantes)

def test_construir_borrador_orden_calcula_total_por_visitante():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import construir_borrador_orden
    except ImportError:
        pytest.fail("La función 'construir_borrador_orden' no está definida o no se puede importar")

    # Arrange
    usuario = {"id": 1, "nombre": "Marco"}
    fecha_visita = date.today()
    visitantes = [
        {"nombre": "Ana", "edad": 25},
        {"nombre": "Luis", "edad": 30},
        {"nombre": "Marta", "edad": 12},
    ]
    tipo_pase = "VIP"
    forma_pago = "TARJETA"

    # motor_precios mock: devuelve distinto monto por edad (para poder validar el cálculo)
    def motor_precios_mock(visitante, tipo_pase):
        if visitante["edad"] < 18:
            return {"monto": 8000, "moneda": "ARS"}
        return {"monto": 15000, "moneda": "ARS"}

    # Act
    borrador = construir_borrador_orden(
        usuario=usuario,
        fecha_visita=fecha_visita,
        visitantes=visitantes,
        tipo_pase=tipo_pase,
        forma_pago=forma_pago,
        motor_precios=motor_precios_mock
    )

    # Assert
    assert isinstance(borrador, dict), "El resultado debe ser un diccionario"
    assert "lineas" in borrador, "El borrador debe incluir las líneas de orden"

    # Verificamos que cada visitante tenga un precio correspondiente al motor
    precios_esperados = [15000, 15000, 8000]
    precios_obtenidos = [linea["precio"]["monto"] for linea in borrador["lineas"]]

    assert precios_obtenidos == precios_esperados, (
        f"Los precios por visitante deberían ser {precios_esperados}, pero se obtuvieron {precios_obtenidos}"
    )

    # Verificamos que el total sea la suma esperada
    total_esperado = sum(precios_esperados)
    assert borrador.get("total", 0) == total_esperado, (
        f"El total del borrador debería ser {total_esperado}"
    )