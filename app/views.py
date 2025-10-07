from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate
from datetime import date, datetime
import json

from .models import Usuario, Compra, Entrada, Parque, Pago
from .services import CompraService


class HomeView(TemplateView):
    """Vista principal del sistema"""
    template_name = 'app/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parques'] = Parque.objects.all()
        return context


@login_required
def comprar_entrada_view(request):
    """Vista para mostrar el formulario de compra de entradas"""
    parques = Parque.objects.all()
    context = {
        'parques': parques,
        'tipos_pase': ['Regular', 'VIP'],
        'formas_pago': ['efectivo', 'tarjeta'],
        'precio_regular': Entrada.PRECIO_REGULAR,
        'precio_vip': Entrada.PRECIO_VIP,
    }
    return render(request, 'app/comprar_entrada.html', context)


@login_required
@require_http_methods(["POST"])
def procesar_compra_view(request):
    """Vista para procesar la compra de entradas"""
    try:
        # Obtener datos del formulario
        fecha_visita_str = request.POST.get('fecha_visita')
        cantidad = int(request.POST.get('cantidad', 0))
        tipo_pase = request.POST.get('tipo_pase')
        forma_pago = request.POST.get('forma_pago')
        parque_id = int(request.POST.get('parque_id'))
        
        # Convertir fecha
        fecha_visita = datetime.strptime(fecha_visita_str, '%Y-%m-%d').date()
        
        # Obtener parque
        parque = get_object_or_404(Parque, id=parque_id)
        
        # Procesar compra usando el servicio
        compra_service = CompraService()
        resultado = compra_service.procesar_compra(
            visitante=request.user,
            fecha_visita=fecha_visita,
            cantidad=cantidad,
            tipo_pase=tipo_pase,
            forma_pago=forma_pago,
            parque=parque
        )
        
        if resultado['success']:
            # Guardar información en la sesión para la confirmación
            request.session['compra_exitosa'] = {
                'entrada_id': resultado['entrada'].id,
                'cantidad': resultado['entrada'].cantidad,
                'fecha_visita': str(resultado['entrada'].fecha_visita),
                'tipo_pase': resultado['entrada'].tipo_pase,
                'monto_total': resultado['entrada'].monto_total,
                'forma_pago': resultado['entrada'].forma_pago,
            }
            
            # Si es pago con tarjeta, redirigir a MercadoPago
            if resultado['redirect_to_mercadopago']:
                return redirect('app:mercadopago_redirect', 
                              transaction_id=resultado['transaction_id'])
            else:
                messages.success(request, 
                    f'Compra realizada exitosamente. {resultado["entrada"].cantidad} '
                    f'entradas para el {resultado["entrada"].fecha_visita}')
                return redirect('app:confirmacion_compra')
        
        else:
            messages.error(request, resultado['error'])
            return redirect('app:comprar_entrada')
            
    except Exception as e:
        messages.error(request, f'Error al procesar la compra: {str(e)}')
        return redirect('app:comprar_entrada')


@login_required
def confirmacion_compra_view(request):
    """Vista para mostrar la confirmación de compra"""
    compra_info = request.session.get('compra_exitosa')
    
    if not compra_info:
        messages.error(request, 'No hay información de compra disponible')
        return redirect('app:home')
    
    # Limpiar la sesión
    del request.session['compra_exitosa']
    
    context = {
        'compra': compra_info
    }
    return render(request, 'app/confirmacion_compra.html', context)


@login_required
def mercadopago_redirect_view(request, transaction_id):
    """Vista para simular redirección a MercadoPago"""
    context = {
        'transaction_id': transaction_id,
        'monto': request.session.get('compra_exitosa', {}).get('monto_total', 0)
    }
    return render(request, 'app/mercadopago_redirect.html', context)


@login_required
def mercadopago_callback_view(request):
    """Vista para manejar el callback de MercadoPago"""
    # En una implementación real, aquí se verificaría el pago con MercadoPago
    status = request.GET.get('status', 'approved')
    
    if status == 'approved':
        messages.success(request, 'Pago procesado exitosamente')
        return redirect('app:confirmacion_compra')
    else:
        messages.error(request, 'Error en el procesamiento del pago')
        return redirect('app:comprar_entrada')


@login_required
def mis_entradas_view(request):
    """Vista para mostrar las entradas del usuario"""
    entradas = Entrada.objects.filter(visitante=request.user).order_by('-created_at')
    context = {
        'entradas': entradas
    }
    return render(request, 'app/mis_entradas.html', context)


# API Views para AJAX
@login_required
def api_validar_fecha_view(request):
    """API para validar si una fecha está disponible"""
    fecha_str = request.GET.get('fecha')
    parque_id = request.GET.get('parque_id')
    
    if not fecha_str or not parque_id:
        return JsonResponse({'valid': False, 'message': 'Parámetros faltantes'})
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        parque = Parque.objects.get(id=parque_id)
        
        is_valid = parque.verificar_fecha_permitida(fecha)
        
        return JsonResponse({
            'valid': is_valid,
            'message': 'Fecha disponible' if is_valid else 'Fecha no disponible'
        })
        
    except (ValueError, Parque.DoesNotExist):
        return JsonResponse({'valid': False, 'message': 'Error en validación'})


@login_required
def api_calcular_total_view(request):
    """API para calcular el total de la compra"""
    cantidad = request.GET.get('cantidad', 0)
    tipo_pase = request.GET.get('tipo_pase', 'Regular')
    
    try:
        cantidad = int(cantidad)
        compra_service = CompraService()
        total = compra_service.calcular_total(cantidad, tipo_pase)
        
        return JsonResponse({
            'success': True,
            'total': total,
            'cantidad': cantidad,
            'tipo_pase': tipo_pase
        })
        
    except (ValueError, Exception) as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def registro_view(request):
    """Vista para registro de usuarios"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            visitante = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            visitante.validar_registro()
            
            # Autenticar y loguear al usuario
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Registro exitoso')
                return redirect('app:home')
                
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'registration/register.html')


def login_view(request):
    """Vista para login de usuarios"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login exitoso')
            return redirect('app:home')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'registration/login.html')
