import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from app.services import CompraService
from app.models import Parque
from unittest.mock import MagicMock
from datetime import date, timedelta

def debug_compra():
    service = CompraService()
    
    # Limpiar datos existentes y crear visitante real
    from app.models import Visitante
    Visitante.objects.filter(email='test@example.com').delete()
    
    visitante = Visitante.objects.create_user(
        username='testuser',
        email='test@example.com',  
        password='testpass123'
    )
    # Los usuarios guardados en DB siempre tienen is_authenticated = True
    
    # Crear parque
    parque = Parque.objects.create(
        nombre='Test Parque',
        dias_abiertos=[0, 1, 2, 3, 4]  # Lunes a viernes
    )
    
    # Fecha futura
    fecha = date.today() + timedelta(days=1)
    
    # Procesar compra
    resultado = service.procesar_compra(
        visitante=visitante,
        fecha_visita=fecha,
        cantidad=3,
        edades_visitantes=[25, 30, 8],
        tipo_pase='VIP',
        forma_pago='efectivo',
        parque=parque
    )
    
    print("Resultado:", resultado)
    
    # Limpiar
    parque.delete()

if __name__ == "__main__":
    debug_compra()