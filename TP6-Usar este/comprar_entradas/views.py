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