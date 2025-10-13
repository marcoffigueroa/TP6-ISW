# tests/unit/test_confirmar_pago.py
import pytest

def test_confirmar_pago_marca_orden_pagada():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import confirmar_pago
    except ImportError:
        pytest.fail("La función 'confirmar_pago' no está definida o no se puede importar")

    # Arrange
    orden_id = 1
    orden_existente = {"id": orden_id, "estado": "PENDIENTE", "lineas": [{}], "fecha_visita": "2025-10-20"}

    # Repositorio fake en memoria
    store = {orden_id: orden_existente}

    def buscar(id_orden):
        return store.get(id_orden)

    def marcar_pagada(id_orden, momento):
        if id_orden in store:
            store[id_orden]["estado"] = "PAGADA"
            store[id_orden]["pagado_en"] = momento

    repositorio_fake = {
        "buscar": buscar,
        "marcar_pagada": marcar_pagada
    }

    # Servicio de mail fake
    mails_enviados = []
    def enviar_confirmacion(orden):
        mails_enviados.append(orden)

    servicio_mail_fake = {"enviar_confirmacion": enviar_confirmacion}
    reloj_fake = {"ahora": lambda: "2025-10-13T10:00:00Z"}

    notificacion_pago = {"id_orden": orden_id, "estado": "aprobado"}

    # Act
    resultado = confirmar_pago(
        notificacion_pago=notificacion_pago,
        repositorio=repositorio_fake,
        servicio_mail=servicio_mail_fake,
        reloj=reloj_fake,
    )

    # Assert
    assert store[orden_id]["estado"] == "PAGADA", "La orden debería quedar marcada como PAGADA"
    assert len(mails_enviados) == 1, "Debería haberse enviado un mail de confirmación"
    assert isinstance(resultado, dict), "El resultado debería ser un diccionario"
    assert resultado.get("cantidad_entradas") == len(orden_existente["lineas"]), \
        "El resultado debe incluir la cantidad de entradas"
    assert resultado.get("fecha_visita") == orden_existente["fecha_visita"], \
        "El resultado debe incluir la fecha de visita"

def test_confirmar_pago_envia_mail_de_confirmacion():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import confirmar_pago
    except ImportError:
        pytest.fail("La función 'confirmar_pago' no está definida o no se puede importar")

    # Arrange
    orden_id = 1
    orden_existente = {"id": orden_id, "estado": "PENDIENTE", "lineas": [{}], "fecha_visita": "2025-10-20"}
    store = {orden_id: orden_existente}

    def buscar(id_orden):
        return store.get(id_orden)

    def marcar_pagada(id_orden, momento):
        if id_orden in store:
            store[id_orden]["estado"] = "PAGADA"
            store[id_orden]["pagado_en"] = momento

    repositorio_fake = {"buscar": buscar, "marcar_pagada": marcar_pagada}

    # Servicio de mail fake: registra si fue llamado
    mail_enviado = {"llamado": False}
    def enviar_confirmacion(orden):
        mail_enviado["llamado"] = True
        mail_enviado["orden"] = orden

    servicio_mail_fake = {"enviar_confirmacion": enviar_confirmacion}
    reloj_fake = {"ahora": lambda: "2025-10-13T10:00:00Z"}

    notificacion_pago = {"id_orden": orden_id, "estado": "aprobado"}

    # Act
    resultado = confirmar_pago(
        notificacion_pago=notificacion_pago,
        repositorio=repositorio_fake,
        servicio_mail=servicio_mail_fake,
        reloj=reloj_fake,
    )

    # Assert
    assert mail_enviado["llamado"], "Debería haberse enviado el mail de confirmación"
    assert store[orden_id]["estado"] == "PAGADA", "La orden debería quedar marcada como PAGADA"
    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    assert resultado.get("fecha_visita") == orden_existente["fecha_visita"], "Debe devolver la fecha de visita"

