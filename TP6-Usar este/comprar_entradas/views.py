from django.shortcuts import render

# Create your views here.

def validar_usuario_registrado(usuario):
    if not usuario or not usuario.get("id"):
        raise ValueError("El usuario no está registrado.")

