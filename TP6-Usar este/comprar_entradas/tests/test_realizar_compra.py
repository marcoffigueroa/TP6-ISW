# tests/unit/test_realizar_compra.py
import pytest
from datetime import date

def test_realizar_compra_tarjeta_redirige_a_mercadopago():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import realizar_compra
    except ImportError:
        pytest.fail("La función 'realizar_compra' no está definida o no se puede importar")

    # Arrange
    usuario = {"id": 1, "nombre": "Marco"}
    fecha_visita = date.today()
    visitantes = [
        {"nombre": "Ana", "edad": 25},
        {"nombre": "Luis", "edad": 30},
    ]
    tipo_pase = "REGULAR"
    forma_pago = "TARJETA"

    # Mock proveedores y servicios
    proveedor_horarios_mock = lambda fecha: True
    motor_precios_mock = lambda visitante, tipo_pase: {"monto": 10000, "moneda": "ARS"}

    repositorio_fake = {
        "guardar_pendiente": lambda borrador: {"id": 1, "estado": "PENDIENTE"}
    }

    enrutador_pagos_mock = {"iniciar_flujo_tarjeta": lambda orden: "https://mercadopago.test/checkout/abc123"}
    servicio_mail_mock = {}  # Simple dict instead of mocker.Mock()
    reloj_fake = {"ahora": lambda: "2025-10-13T10:00:00Z"}

    # Act
    resultado = realizar_compra(
        usuario=usuario,
        fecha_visita=fecha_visita,
        cantidad_entradas=len(visitantes),
        visitantes=visitantes,
        tipo_pase=tipo_pase,
        forma_pago=forma_pago,
        proveedor_horarios=proveedor_horarios_mock,
        motor_precios=motor_precios_mock,
        repositorio=repositorio_fake,
        enrutador_pagos=enrutador_pagos_mock,
        servicio_mail=servicio_mail_mock,
        reloj=reloj_fake,
    )

    # Assert
    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    assert "redirect_url" in resultado, "Debe incluir una URL de redirección"
    assert resultado["redirect_url"].startswith("https://mercadopago"), \
        "La URL debe apuntar a Mercado Pago"
