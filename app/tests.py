import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock, MagicMock
from datetime import date, timedelta
import json

from .models import Usuario, Compra, Entrada, Parque, Pago
from .services import CompraService, EmailService

User = get_user_model()


@pytest.mark.django_db
class TestCriteriosAceptacionCompletos:
    """Tests para TODOS los criterios de aceptación de la user story"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.compra_service = CompraService()
        
        # Crear usuario real 
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Los usuarios guardados en DB siempre tienen is_authenticated = True
        
        self.parque = Parque.objects.create(
            nombre='Parque Principal',
            dias_abiertos=[0, 1, 2, 3, 4]  # Lunes a viernes
        )
        
        # Fecha válida (mañana)
        self.fecha_valida = date.today() + timedelta(days=1)
        
    # CRITERIO 1: Debe indicar fecha, cantidad, edad de cada visitante y tipo de pase
    def test_debe_indicar_fecha_cantidad_edades_tipo_pase(self):
        """
        CRITERIO 1: Debe indicar la fecha de visita deseada, la cantidad de entradas requeridas, 
        la edad de cada visitante y tipo de pase (VIP o regular).
        """
        edades_visitantes = [25, 30, 8]  # 3 visitantes con sus edades
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=3,
            edades_visitantes=edades_visitantes,
            tipo_pase='VIP',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        entrada = resultado['entrada']
        assert entrada.fecha_visita == self.fecha_valida
        assert entrada.cantidad == 3
        assert entrada.edades_visitantes == edades_visitantes
        assert entrada.tipo_pase == 'VIP'
    
    def test_falla_si_cantidad_no_coincide_con_edades(self):
        """
        CRITERIO 1: Debe fallar si la cantidad no coincide con el número de edades
        """
        edades_visitantes = [25, 30]  # Solo 2 edades
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=3,  # Pero dice 3 entradas
            edades_visitantes=edades_visitantes,
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is False
        assert 'La cantidad de entradas debe coincidir con el número de edades' in resultado['error']
    
    def test_falla_si_edad_invalida(self):
        """
        CRITERIO 1: Debe fallar si hay edades inválidas (menores a 0 o mayores a 120)
        """
        edades_visitantes = [25, -5, 130]  # Edades inválidas
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=3,
            edades_visitantes=edades_visitantes,
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is False
        assert 'Las edades deben estar entre 0 y 120 años' in resultado['error']
    
    # CRITERIO 2: La fecha puede ser del día actual o futuro
    def test_fecha_puede_ser_hoy(self):
        """
        CRITERIO 2: La fecha de visita puede ser del día actual
        """
        # Crear parque que esté abierto hoy
        dia_hoy = date.today().weekday()
        parque_abierto_hoy = Parque.objects.create(
            nombre='Parque Abierto Hoy',
            dias_abiertos=[dia_hoy]
        )
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=date.today(),  # Fecha de hoy
            cantidad=2,
            edades_visitantes=[25, 30],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=parque_abierto_hoy
        )
        
        assert resultado['success'] is True
        assert resultado['entrada'].fecha_visita == date.today()
    
    def test_fecha_puede_ser_futura(self):
        """
        CRITERIO 2: La fecha de visita puede ser futura
        """
        # Buscar próximo día laborable (lunes = 0)
        today = date.today()
        days_ahead = 0 - today.weekday()  # 0 = lunes
        if days_ahead <= 0:
            days_ahead += 7
        fecha_futura = today + timedelta(days_ahead + 7)  # Lunes de la próxima semana
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=fecha_futura,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['entrada'].fecha_visita == fecha_futura
    
    def test_falla_fecha_pasada(self):
        """
        CRITERIO 2: Debe fallar con fecha pasada
        """
        fecha_pasada = date.today() - timedelta(days=1)
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=fecha_pasada,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is False
        assert 'no está disponible' in resultado['error']
    
    # CRITERIO 3: Debe enviar mensaje de confirmación vía mail
    @patch('app.services.EmailService.enviar_confirmacion')
    def test_debe_enviar_confirmacion_email(self, mock_email):
        """
        CRITERIO 3: Debe enviar un mensaje de confirmación vía mail
        """
        mock_email.return_value = True
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=2,
            edades_visitantes=[25, 30],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['email_enviado'] is True
        mock_email.assert_called_once()
    
    # CRITERIO 4: Debe redirigir a MercadoPago si pago es con tarjeta
    @patch('app.services.EmailService.enviar_confirmacion')
    def test_redirige_mercadopago_con_tarjeta(self, mock_email):
        """
        CRITERIO 4: Debe redirigir a mercado pago al confirmar la compra si el pago es con tarjeta
        """
        mock_email.return_value = True
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='tarjeta',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['redirect_to_mercadopago'] is True
        assert resultado['transaction_id'] is not None
    
    @patch('app.services.EmailService.enviar_confirmacion')
    def test_no_redirige_mercadopago_con_efectivo(self, mock_email):
        """
        CRITERIO 4: No debe redirigir a MercadoPago si pago es en efectivo
        """
        mock_email.return_value = True
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['redirect_to_mercadopago'] is False
        assert resultado['transaction_id'] is None
    
    # CRITERIO 5: La fecha debe estar dentro de los días abiertos del parque
    def test_fecha_debe_estar_en_dias_abiertos(self):
        """
        CRITERIO 5: La fecha de la visita debe estar dentro de los días en que el parque está abierto
        """
        # Parque solo abierto lunes (0)
        parque_solo_lunes = Parque.objects.create(
            nombre='Parque Solo Lunes',
            dias_abiertos=[0]  # Solo lunes
        )
        
        # Buscar próximo martes
        today = date.today()
        days_ahead = 1 - today.weekday()  # 1 = martes
        if days_ahead <= 0:
            days_ahead += 7
        next_tuesday = today + timedelta(days_ahead)
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=next_tuesday,  # Martes (parque cerrado)
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=parque_solo_lunes
        )
        
        assert resultado['success'] is False
        assert 'no está disponible' in resultado['error']
    
    # CRITERIO 6: Debe seleccionar forma de pago (efectivo o tarjeta)
    def test_debe_seleccionar_forma_pago_efectivo(self):
        """
        CRITERIO 6: Debe seleccionar forma de pago: efectivo
        """
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['entrada'].forma_pago == 'efectivo'
    
    def test_debe_seleccionar_forma_pago_tarjeta(self):
        """
        CRITERIO 6: Debe seleccionar forma de pago: tarjeta
        """
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='tarjeta',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['entrada'].forma_pago == 'tarjeta'
    
    def test_falla_forma_pago_invalida(self):
        """
        CRITERIO 6: Debe fallar con forma de pago inválida
        """
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='crypto',  # Forma de pago inválida
            parque=self.parque
        )
        
        assert resultado['success'] is False
        assert 'forma de pago válida' in resultado['error']
    
    # CRITERIO 7: Cantidad no debe ser mayor a 10
    def test_cantidad_no_mayor_10(self):
        """
        CRITERIO 7: La cantidad de entradas requeridas no debe ser mayor a 10
        """
        edades_11_personas = [25] * 11  # 11 personas
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=11,
            edades_visitantes=edades_11_personas,
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is False
        assert 'La cantidad debe ser entre 1 y 10' in resultado['error']
    
    def test_cantidad_maxima_10_permitida(self):
        """
        CRITERIO 7: La cantidad máxima de 10 debe estar permitida
        """
        edades_10_personas = [25] * 10  # 10 personas
        
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=10,
            edades_visitantes=edades_10_personas,
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['entrada'].cantidad == 10
    
    # CRITERIO 8: Al finalizar debe informar cantidad y fecha
    def test_debe_informar_cantidad_y_fecha_compra(self):
        """
        CRITERIO 8: Al finalizar la compra se debe informar la cantidad de entradas compradas y la fecha
        """
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=3,
            edades_visitantes=[25, 30, 8],
            tipo_pase='VIP',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        
        # Verificar que se puede obtener el resumen
        resumen = self.compra_service.obtener_resumen_compra(resultado['entrada'])
        assert resumen['cantidad_entradas'] == 3
        assert resumen['fecha_visita'] == self.fecha_valida
        assert resumen['tipo_pase'] == 'VIP'
        assert resumen['fecha_compra'] is not None
    
    # CRITERIO 9: Solo usuarios registrados pueden comprar
    def test_solo_usuarios_registrados_pueden_comprar(self):
        """
        CRITERIO 9: Se debe permitir la compra de entradas solo a usuarios registrados
        """
        # Usuario no autenticado
        visitante_no_auth = MagicMock()
        visitante_no_auth.is_authenticated = False
        
        resultado = self.compra_service.procesar_compra(
            visitante=visitante_no_auth,
            fecha_visita=self.fecha_valida,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is False
        assert 'debe estar autenticado' in resultado['error']
    
    def test_usuarios_registrados_pueden_comprar(self):
        """
        CRITERIO 9: Usuarios registrados y autenticados SÍ pueden comprar
        """
        # Usuario autenticado real (ya tenemos self.visitante que es real y autenticado)
        resultado = self.compra_service.procesar_compra(
            visitante=self.usuario,
            fecha_visita=self.fecha_valida,
            cantidad=1,
            edades_visitantes=[25],
            tipo_pase='Regular',
            forma_pago='efectivo',
            parque=self.parque
        )
        
        assert resultado['success'] is True
        assert resultado['entrada'] is not None


@pytest.mark.django_db
class TestValidacionEdades:
    """Tests específicos para validación de edades"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.compra_service = CompraService()
    
    def test_validar_edades_correctas(self):
        """Test validación de edades correctas"""
        edades_validas = [0, 5, 18, 25, 65, 120]  # Rango válido 0-120
        resultado = self.compra_service.validar_edades_visitantes(edades_validas, 6)
        assert resultado is True
    
    def test_falla_edad_negativa(self):
        """Test falla con edad negativa"""
        edades_invalidas = [25, -1, 30]
        with pytest.raises(ValidationError, match="Las edades deben estar entre 0 y 120 años"):
            self.compra_service.validar_edades_visitantes(edades_invalidas, 3)
    
    def test_falla_edad_mayor_120(self):
        """Test falla con edad mayor a 120"""
        edades_invalidas = [25, 121, 30]
        with pytest.raises(ValidationError, match="Las edades deben estar entre 0 y 120 años"):
            self.compra_service.validar_edades_visitantes(edades_invalidas, 3)
    
    def test_falla_cantidad_no_coincide_edades(self):
        """Test falla cuando cantidad no coincide con número de edades"""
        edades = [25, 30]  # 2 edades
        cantidad = 3  # Pero dice 3 entradas
        
        with pytest.raises(ValidationError, match="La cantidad de entradas debe coincidir con el número de edades"):
            self.compra_service.validar_edades_visitantes(edades, cantidad)
    
    def test_falla_lista_edades_vacia(self):
        """Test falla con lista de edades vacía"""
        edades = []
        cantidad = 1
        
        with pytest.raises(ValidationError, match="Debe proporcionar las edades de todos los visitantes"):
            self.compra_service.validar_edades_visitantes(edades, cantidad)
