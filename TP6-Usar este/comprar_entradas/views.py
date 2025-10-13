from django.shortcuts import render

# Create your views here.

def validar_usuario_registrado(usuario):
    if not usuario or not usuario.get("id"):
        raise ValueError("El usuario no está registrado.")

def validar_cantidad_entradas(cantidad):
    # Validar que la cantidad no supere el límite máximo de 10
    if cantidad > 10:
        raise ValueError("La cantidad de entradas supera el máximo permitido")
    
    # Por ahora retorna True para casos válidos (para que pase el primer test)
    return True

def validar_fecha_visita(fecha, feriados=None):
    if feriados is None:
        feriados = []
    
    # Validar que no sea lunes (weekday() == 0 es lunes)
    if fecha.weekday() == 0:
        raise ValueError("El parque está cerrado los lunes")
    
    # Validar que no sea feriado
    if fecha in feriados:
        raise ValueError("El parque está cerrado en feriados")
    
    # Si pasa todas las validaciones, la fecha es válida
    return True

def validar_forma_pago(forma_pago):
    # Definir las formas de pago válidas
    formas_validas = ["EFECTIVO", "TARJETA"]
    
    # Validar que la forma de pago esté en la lista de válidas
    if forma_pago not in formas_validas:
        raise ValueError("Forma de pago no válida")
    
    # Si es válida, no hace nada (no lanza excepción)
    return True

def validar_tipo_pase(tipo_pase):
    # Definir los tipos de pase válidos
    tipos_validos = ["VIP", "REGULAR"]
    
    # Validar que el tipo de pase esté en la lista de válidos
    if tipo_pase not in tipos_validos:
        raise ValueError("Tipo de pase no válido")
    
    # Si es válido, no hace nada (no lanza excepción)
    return True

def validar_datos_visitantes(visitantes):
    # Validar que cada visitante tenga los datos requeridos
    for visitante in visitantes:
        if "edad" not in visitante or "nombre" not in visitante:
            raise ValueError("Faltan datos del visitante")
    return True

def construir_borrador_orden(usuario, fecha_visita, visitantes, tipo_pase, forma_pago, motor_precios):
    # Lógica mínima para hacer pasar el test
    lineas = []
    total = 0
    
    for visitante in visitantes:
        precio = motor_precios(visitante, tipo_pase)
        linea = visitante.copy()  # Copiar datos del visitante
        linea["precio"] = precio  # Agregar precio
        lineas.append(linea)
        total += precio["monto"]  # Sumar al total
    
    return {
        "usuario": usuario,
        "fecha_visita": fecha_visita,
        "forma_pago": forma_pago,
        "tipo_pase": tipo_pase,
        "lineas": lineas,
        "total": total
    }

def calcular_total(borrador, motor_precios):
    # Lógica mínima para hacer pasar el test
    total = 0
    for linea in borrador["lineas"]:
        total += linea["precio"]["monto"]
    return total

def realizar_compra(usuario, fecha_visita, cantidad_entradas, visitantes, tipo_pase, forma_pago, 
                   proveedor_horarios, motor_precios, repositorio, enrutador_pagos, servicio_mail, reloj):
    # Lógica mínima para hacer pasar el test
    # Validar usuario registrado
    validar_usuario_registrado(usuario)
    
    # Validar cantidad de entradas
    validar_cantidad_entradas(cantidad_entradas)
    
    # Validar que el parque esté abierto en la fecha de visita
    if not proveedor_horarios(fecha_visita):
        raise ValueError("El parque está cerrado en la fecha seleccionada")
    
    # Para forma_pago = "TARJETA", usar el enrutador de pagos
    if forma_pago == "TARJETA":
        # Crear un borrador básico para pasar al enrutador
        borrador = {"id": 1, "estado": "PENDIENTE"}
        redirect_url = enrutador_pagos["iniciar_flujo_tarjeta"](borrador)
        return {"redirect_url": redirect_url}
    
    # Para forma_pago = "EFECTIVO", devolver instrucciones
    elif forma_pago == "EFECTIVO":
        return {
            "instrucciones": "Dirigirse a la boletería del parque para completar el pago en efectivo",
            "redirect_url": None
        }
    
    # Para otros casos, retornar algo básico
    return {"redirect_url": "https://mercadopago.test/default"}