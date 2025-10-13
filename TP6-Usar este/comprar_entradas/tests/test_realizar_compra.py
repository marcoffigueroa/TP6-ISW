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

def test_realizar_compra_efectivo_devuelve_instrucciones():
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
    forma_pago = "EFECTIVO"

    # Mock proveedores y servicios
    proveedor_horarios_mock = lambda fecha: True
    motor_precios_mock = lambda visitante, tipo_pase: {"monto": 10000, "moneda": "ARS"}

    repositorio_fake = {
        "guardar_pendiente": lambda borrador: {"id": 1, "estado": "EN_ESPERA_DE_PAGO"}
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
    assert "instrucciones" in resultado, "Debe incluir las instrucciones de pago"
    assert "boletería" in resultado["instrucciones"].lower(), \
        "Las instrucciones deben indicar el pago en boletería"
    assert "redirect_url" not in resultado or resultado["redirect_url"] is None, \
        "No debe existir redirección cuando el pago es en efectivo"
    
def test_realizar_compra_falla_si_usuario_no_registrado():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import realizar_compra
    except ImportError:
        pytest.fail("La función 'realizar_compra' no está definida o no se puede importar")

    # Arrange: usuario sin id (no registrado)
    usuario = {"nombre": "Visitante"}  # Falta "id"
    fecha_visita = date.today()
    visitantes = [
        {"nombre": "Ana", "edad": 25},
        {"nombre": "Luis", "edad": 30},
    ]
    tipo_pase = "REGULAR"
    forma_pago = "TARJETA"

    # Mocks simples implementados dentro del test
    proveedor_horarios_mock = lambda fecha: True
    motor_precios_mock = lambda visitante, tipo_pase: {"monto": 10000, "moneda": "ARS"}

    repositorio_fake = {
        "guardar_pendiente": lambda borrador: {"id": 1, "estado": "PENDIENTE"}
    }

    enrutador_pagos_mock = {
        "iniciar_flujo_tarjeta": lambda orden: "https://mercadopago.test/checkout/abc123"
    }

    # Servicio de mail fake local
    def enviar_confirmacion(orden):
        raise AssertionError("No debería llamarse a enviar_confirmacion en este test")

    servicio_mail_fake = {"enviar_confirmacion": enviar_confirmacion}

    reloj_fake = {"ahora": lambda: "2025-10-13T10:00:00Z"}

    # Act & Assert: debe lanzar una excepción por usuario no registrado
    with pytest.raises(Exception):
        realizar_compra(
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
            servicio_mail=servicio_mail_fake,
            reloj=reloj_fake,
        )


def test_realizar_compra_falla_si_fecha_cerrada():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import realizar_compra
    except ImportError:
        pytest.fail("La función 'realizar_compra' no está definida o no se puede importar")

    # Arrange
    usuario = {"id": 1, "nombre": "Marco"}
    fecha_visita = date.today()
    visitantes = [{"nombre": "Ana", "edad": 25}]
    tipo_pase = "REGULAR"
    forma_pago = "TARJETA"

    # Mocks simples
    proveedor_horarios_mock = lambda fecha: False  # parque cerrado
    motor_precios_mock = lambda visitante, tipo_pase: {"monto": 10000, "moneda": "ARS"}
    repositorio_fake = {
        "guardar_pendiente": lambda borrador: {"id": 1, "estado": "PENDIENTE"}
    }
    enrutador_pagos_mock = {
        "iniciar_flujo_tarjeta": lambda orden: "https://mercadopago.test/checkout/abc123"
    }

    def enviar_confirmacion(orden):
        raise AssertionError("No debería enviarse mail en caso de parque cerrado")

    servicio_mail_fake = {"enviar_confirmacion": enviar_confirmacion}
    reloj_fake = {"ahora": lambda: "2025-10-13T10:00:00Z"}

    # Act & Assert
    with pytest.raises(Exception):
        realizar_compra(
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
            servicio_mail=servicio_mail_fake,
            reloj=reloj_fake,
        )

def test_realizar_compra_falla_si_cantidad_mayor_a_limite():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import realizar_compra
    except ImportError:
        pytest.fail("La función 'realizar_compra' no está definida o no se puede importar")

    # Arrange
    usuario = {"id": 1, "nombre": "Marco"}
    fecha_visita = date.today()
    # 11 visitantes (supera el límite de 10)
    visitantes = [{"nombre": f"Visitante{i}", "edad": 20+i} for i in range(11)]
    tipo_pase = "REGULAR"
    forma_pago = "TARJETA"

    # Mocks simples
    proveedor_horarios_mock = lambda fecha: True
    motor_precios_mock = lambda visitante, tipo_pase: {"monto": 10000, "moneda": "ARS"}
    repositorio_fake = {
        "guardar_pendiente": lambda borrador: {"id": 1, "estado": "PENDIENTE"}
    }
    enrutador_pagos_mock = {
        "iniciar_flujo_tarjeta": lambda orden: "https://mercadopago.test/checkout/abc123"
    }

    def enviar_confirmacion(orden):
        raise AssertionError("No debería enviarse mail cuando se supera el límite de entradas")

    servicio_mail_fake = {"enviar_confirmacion": enviar_confirmacion}
    reloj_fake = {"ahora": lambda: "2025-10-13T10:00:00Z"}

    # Act & Assert
    with pytest.raises(Exception):
        realizar_compra(
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
            servicio_mail=servicio_mail_fake,
            reloj=reloj_fake,
        )

def test_realizar_compra_falla_si_forma_pago_no_especificada():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import realizar_compra
    except ImportError:
        pytest.fail("La función 'realizar_compra' no está definida o no se puede importar")

    # Arrange: usuario registrado pero sin forma de pago
    usuario = {"id": 1, "nombre": "Marco"}
    fecha_visita = date.today()
    visitantes = [
        {"nombre": "Ana", "edad": 25},
        {"nombre": "Luis", "edad": 30},
    ]
    tipo_pase = "REGULAR"
    forma_pago = None  # No especificada

    # Mocks simples
    proveedor_horarios_mock = lambda fecha: True
    motor_precios_mock = lambda visitante, tipo_pase: {"monto": 10000, "moneda": "ARS"}
    repositorio_fake = {
        "guardar_pendiente": lambda borrador: {"id": 1, "estado": "PENDIENTE"}
    }
    enrutador_pagos_mock = {
        "iniciar_flujo_tarjeta": lambda orden: "https://mercadopago.test/checkout/abc123"
    }

    def enviar_confirmacion(orden):
        raise AssertionError("No debería enviarse mail cuando la forma de pago no está definida")

    servicio_mail_fake = {"enviar_confirmacion": enviar_confirmacion}
    reloj_fake = {"ahora": lambda: "2025-10-13T10:00:00Z"}

    # Act & Assert: debe fallar al no tener forma de pago
    with pytest.raises(Exception):
        realizar_compra(
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
            servicio_mail=servicio_mail_fake,
            reloj=reloj_fake,
        )