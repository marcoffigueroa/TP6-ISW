from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Vistas principales
    path('', views.HomeView.as_view(), name='home'),
    path('comprar/', views.comprar_entrada_view, name='comprar_entrada'),
    path('procesar-compra/', views.procesar_compra_view, name='procesar_compra'),
    path('confirmacion/', views.confirmacion_compra_view, name='confirmacion_compra'),
    path('mis-entradas/', views.mis_entradas_view, name='mis_entradas'),
    
    # MercadoPago
    path('mercadopago/<str:transaction_id>/', views.mercadopago_redirect_view, name='mercadopago_redirect'),
    path('mercadopago/callback/', views.mercadopago_callback_view, name='mercadopago_callback'),
    
    # API endpoints
    path('api/validar-fecha/', views.api_validar_fecha_view, name='api_validar_fecha'),
    path('api/calcular-total/', views.api_calcular_total_view, name='api_calcular_total'),
    
    # Autenticación
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
]