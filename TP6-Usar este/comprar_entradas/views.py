from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import ComprarEntradasForm
import datetime
import json

# Importar los feriados del nuevo archivo
from .constants import FERIADOS

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
    
    # Validar forma de pago
    validar_forma_pago(forma_pago)
    
    # Validar datos de visitantes
    validar_datos_visitantes(visitantes)
    
    # Validar que el parque esté abierto en la fecha de visita
    if not proveedor_horarios(fecha_visita):
        raise ValueError("El parque está cerrado en la fecha seleccionada")
    
    # Para forma_pago = "TARJETA", usar el enrutador de pagos
    if forma_pago == "TARJETA":
        # Crear un borrador usando el motor_precios
        borrador = construir_borrador_orden(usuario, fecha_visita, visitantes, tipo_pase, forma_pago, motor_precios)
        # Guardar en repositorio si tiene método guardar_pendiente
        if "guardar_pendiente" in repositorio:
            orden = repositorio["guardar_pendiente"](borrador)
        else:
            orden = {"id": 1, "estado": "PENDIENTE"}
        
        redirect_url = enrutador_pagos["iniciar_flujo_tarjeta"](orden)
        return {"redirect_url": redirect_url}
    
    # Para forma_pago = "EFECTIVO", devolver instrucciones
    elif forma_pago == "EFECTIVO":
        # Crear borrador y guardarlo si es necesario
        borrador = construir_borrador_orden(usuario, fecha_visita, visitantes, tipo_pase, forma_pago, motor_precios)
        if "guardar_pendiente" in repositorio:
            orden = repositorio["guardar_pendiente"](borrador)
        
        return {
            "instrucciones": "Dirigirse a la boletería del parque para completar el pago en efectivo",
            "redirect_url": None
        }
    
    # Para otros casos, retornar algo básico
    return {"redirect_url": "https://mercadopago.test/default"}

def confirmar_pago(notificacion_pago, repositorio, servicio_mail, reloj):
    # Lógica mínima para hacer pasar el test
    # Obtener el ID de la orden desde la notificación
    orden_id = notificacion_pago["id_orden"]
    
    # Buscar la orden en el repositorio
    orden = repositorio["buscar"](orden_id)
    
    # Validar que la orden existe
    if orden is None:
        raise ValueError("La orden no existe")
    
    # Marcar la orden como pagada
    momento = reloj["ahora"]()
    repositorio["marcar_pagada"](orden_id, momento)
    
    # Enviar confirmación por email
    servicio_mail["enviar_confirmacion"](orden)
    
    # Retornar información de la orden
    return {
        "cantidad_entradas": len(orden["lineas"]),
        "fecha_visita": orden["fecha_visita"]
    }

# Motor de precios de ejemplo (implementación simple)
def motor_precios_simple(visitante, tipo_pase):
    """
    Motor de precios básico que calcula el precio según edad y tipo de pase.
    """
    edad = visitante.get('edad', 0)
    
    # Precios base
    if tipo_pase == "VIP":
        precio_base = 5000
    else:  # REGULAR
        precio_base = 3000
    
    # Descuentos por edad
    if edad < 12:  # Niños
        monto = precio_base * 0.5
    elif edad >= 65:  # Tercera edad
        monto = precio_base * 0.7
    else:  # Adultos
        monto = precio_base
    
    return {"monto": monto}

# Proveedores de servicios de ejemplo
def proveedor_horarios_simple(fecha):
    """
    Verifica si el parque está abierto en una fecha específica.
    """
    # El parque está cerrado los lunes
    if fecha.weekday() == 0:
        return False
    return True

def enrutador_pagos_simple():
    """
    Simulador de enrutador de pagos.
    """
    return {
        "iniciar_flujo_tarjeta": lambda borrador: "https://mercadopago.test/checkout/123"
    }

def repositorio_simple():
    """
    Simulador de repositorio de órdenes.
    """
    return {
        "buscar": lambda orden_id: {"id": orden_id, "lineas": [], "fecha_visita": datetime.date.today()},
        "marcar_pagada": lambda orden_id, momento: True
    }

def servicio_mail_simple():
    """
    Simulador de servicio de email.
    """
    return {
        "enviar_confirmacion": lambda orden: True
    }

def reloj_simple():
    """
    Simulador de servicio de tiempo.
    """
    return {
        "ahora": lambda: datetime.datetime.now()
    }

def comprar_entradas_view(request):
    """
    Vista principal para el formulario de compra de entradas.
    """
    if request.method == 'POST':
        form = ComprarEntradasForm(request.POST)
        
        if form.is_valid():
            try:
                # Extraer datos del formulario
                usuario = {
                    "id": 1,  # Simulamos usuario registrado
                    "nombre": form.cleaned_data['usuario_nombre'],
                    "email": form.cleaned_data['usuario_email']
                }
                
                fecha_visita = form.cleaned_data['fecha_visita']
                tipo_pase = form.cleaned_data['tipo_pase']
                forma_pago = form.cleaned_data['forma_pago']
                cantidad_visitantes = form.cleaned_data['cantidad_visitantes']
                
                # VALIDAR FECHA DE VISITA CON FERIADOS
                validar_fecha_visita(fecha_visita, FERIADOS)
                
                # Extraer datos de visitantes del POST
                visitantes = []
                for i in range(cantidad_visitantes):
                    nombre = request.POST.get(f'visitante_{i}_nombre', '')
                    edad_str = request.POST.get(f'visitante_{i}_edad', '0')
                    
                    if nombre and edad_str.isdigit():
                        visitantes.append({
                            'nombre': nombre,
                            'edad': int(edad_str)
                        })
                
                # Usar las funciones existentes con dependencias simuladas
                resultado = realizar_compra(
                    usuario=usuario,
                    fecha_visita=fecha_visita,
                    cantidad_entradas=cantidad_visitantes,
                    visitantes=visitantes,
                    tipo_pase=tipo_pase,
                    forma_pago=forma_pago,
                    proveedor_horarios=proveedor_horarios_simple,
                    motor_precios=motor_precios_simple,  # Agregar motor_precios
                    repositorio=repositorio_simple(),
                    enrutador_pagos=enrutador_pagos_simple(),
                    servicio_mail=servicio_mail_simple(),
                    reloj=reloj_simple()
                )
                
                # Manejar el resultado según la forma de pago
                if forma_pago == "TARJETA":
                    messages.success(request, f"Redirigiendo al pago con tarjeta: {resultado['redirect_url']}")
                elif forma_pago == "EFECTIVO":
                    messages.success(request, resultado['instrucciones'])
                
                # Construir borrador para mostrar resumen
                borrador = construir_borrador_orden(
                    usuario=usuario,
                    fecha_visita=fecha_visita,
                    visitantes=visitantes,
                    tipo_pase=tipo_pase,
                    forma_pago=forma_pago,
                    motor_precios=motor_precios_simple
                )
                
                messages.info(request, f"Total de la compra: ${borrador['total']}")
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error inesperado: {str(e)}")
    
    else:
        form = ComprarEntradasForm()
    
    # Pasar feriados al template para validación en JavaScript
    feriados_json = json.dumps([f.strftime('%Y-%m-%d') for f in FERIADOS])
    
    return render(request, 'comprar_entradas.html', {
        'form': form,
        'feriados_json': feriados_json
    })