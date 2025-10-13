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