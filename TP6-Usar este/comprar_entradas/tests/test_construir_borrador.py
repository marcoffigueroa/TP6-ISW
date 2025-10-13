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
