from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from typing import Dict, Any
import uuid
import logging

from .interfaces import IPaymentService, INotificacionService
from .models import Usuario, Compra, Entrada, Parque, Pago

logger = logging.getLogger(__name__)


class MercadoPago(IPaymentService):
    """
    Implementación de IPaymentService para MercadoPago
    Gestiona el flujo de pago electrónico
    """
    
    def procesar_pago(self, monto: float, forma_pago: int) -> Dict[str, Any]:
        """
        Procesa el pago según la forma especificada
        
        Args:
            monto: Monto total a procesar
            forma_pago: 1 = efectivo, 2 = tarjeta
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            self.monto = monto
            self.forma_de_pago = forma_pago
            
            if forma_pago == 2:  # Tarjeta
                # Simular procesamiento con MercadoPago
                # En una implementación real, aquí iría la integración con la API
                self.id_transaccion_externa = str(uuid.uuid4())
                self.estado = 2  # PROCESADO
                
                return {
                    'success': True,
                    'transaction_id': self.id_transaccion_externa,
                    'redirect_to_mercadopago': True,
                    'estado': self.estado
                }
            elif forma_pago == 1:  # Efectivo
                # Pago en efectivo se procesa directamente
                self.estado = 2  # PROCESADO
                
                return {
                    'success': True,
                    'transaction_id': None,
                    'redirect_to_mercadopago': False,
                    'estado': self.estado
                }
            else:
                self.estado = 3  # FALLIDO
                return {
                    'success': False,
                    'error': 'Forma de pago no válida',
                    'estado': self.estado
                }
                
        except Exception as e:
            logger.error(f"Error procesando pago: {str(e)}")
            self.estado = 3  # FALLIDO
            return {
                'success': False,
                'error': 'Error interno del procesador de pagos',
                'estado': self.estado
            }


class EmailService(INotificacionService):
    """
    Implementación de INotificacionService para notificaciones por email
    Envía la confirmación por correo electrónico tras la compra exitosa
    """
    
    def enviar_confirmacion(self, usuario: Usuario, compra: Compra) -> bool:
        """
        Envía confirmación al usuario tras una compra exitosa
        
        Args:
            usuario: Instancia del usuario
            compra: Instancia de la compra realizada
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            subject = f'Confirmación de compra #{compra.id}'
            
            # Construir detalles de las entradas
            entradas_detalle = ""
            for entrada in compra.entradas.all():
                tipo_str = "VIP" if entrada.tipo_pase == Entrada.VIP else "Regular"
                entradas_detalle += f"- Entrada {tipo_str}: {entrada.fecha_visita} (Edad: {entrada.edad_visitante}) - ${entrada.precio}\n"
            
            message = f"""
            Hola {usuario.username},
            
            Tu compra ha sido confirmada exitosamente.
            
            Detalles de la compra:
            - Número de compra: #{compra.id}
            - Fecha de compra: {compra.fecha_compra.strftime('%Y-%m-%d %H:%M')}
            - Parque: {compra.parque.nombre}
            - Monto total: ${compra.monto_total}
            
            Entradas compradas:
            {entradas_detalle}
            
            ¡Te esperamos en el parque!
            
            Saludos,
            Equipo del Parque
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False,
            )
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False


class CompraService:
    """
    Clase CompraService - Capa de negocio responsable de ejecutar el flujo completo de compra
    
    Atributos:
    - parque: Parque
    - paymentService: IPaymentService  
    - notificacionService: INotificacionService
    
    Rol: Ejecuta validaciones, pago y confirmación
    """
    
    def __init__(self, parque: Parque = None, 
                 payment_service: IPaymentService = None,
                 notificacion_service: INotificacionService = None):
        self.parque = parque
        self.payment_service = payment_service or MercadoPago()
        self.notificacion_service = notificacion_service or EmailService()
    
    def comprar(self, compra: Compra, forma_pago: int = None) -> Dict[str, Any]:
        """
        Método principal para procesar una compra
        
        Args:
            compra: Instancia de Compra con todas las entradas
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            # 1. Validar usuario
            if not compra.usuario.is_authenticated:
                raise ValidationError("El usuario debe estar autenticado")
            
            # 2. Validar cada entrada
            for entrada in compra.entradas.all():
                self._validar_entrada(entrada, compra.parque)
                
            # 3. Calcular monto total
            monto_total = compra.calcular_monto_total()
            
            # 4. Determinar forma de pago
            if forma_pago is None:
                forma_pago = Pago.TARJETA  # Default tarjeta, se puede configurar
            
            # 5. Procesar pago
            resultado_pago = self.payment_service.procesar_pago(monto_total, forma_pago)
            
            if not resultado_pago['success']:
                raise ValidationError(f"Error en el pago: {resultado_pago.get('error', 'Error desconocido')}")
            
            # 6. Crear registro de pago
            pago = Pago.objects.create(
                compra=compra,
                forma_de_pago=forma_pago,
                estado=resultado_pago['estado'],
                monto=monto_total,
                id_transaccion_externa=resultado_pago.get('transaction_id')
            )
            
            # 7. Enviar notificación
            email_enviado = self.notificacion_service.enviar_confirmacion(compra.usuario, compra)
            
            if not email_enviado:
                logger.warning(f"No se pudo enviar email de confirmación para compra {compra.id}")
            
            return {
                'success': True,
                'compra': compra,
                'pago': pago,
                'email_enviado': email_enviado,
                'redirect_to_mercadopago': resultado_pago.get('redirect_to_mercadopago', False),
                'transaction_id': resultado_pago.get('transaction_id')
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'compra': None,
                'pago': None
            }
        except Exception as e:
            logger.error(f"Error inesperado en proceso de compra: {str(e)}")
            return {
                'success': False,
                'error': 'Error interno del servidor',
                'compra': None,
                'pago': None
            }
    
    def _validar_entrada(self, entrada: Entrada, parque: Parque):
        """Validar una entrada individual"""
        # Validar edad
        if entrada.edad_visitante < 0 or entrada.edad_visitante > 120:
            raise ValidationError("La edad debe estar entre 0 y 120 años")
        
        # Validar fecha con el parque
        if not parque.esta_abierto(entrada.fecha_visita):
            raise ValidationError("La fecha seleccionada no está disponible en el parque")
        
        return True
    
    # Métodos de retrocompatibilidad para los tests existentes
    def procesar_compra(self, visitante, fecha_visita, cantidad, edades_visitantes, tipo_pase, forma_pago, parque):
        """
        Método de retrocompatibilidad para los tests existentes
        Adapta los parámetros individuales al nuevo modelo de dominio
        """
        try:
            # Validaciones básicas
            if not hasattr(visitante, 'is_authenticated') or not visitante.is_authenticated:
                raise ValidationError("El usuario debe estar autenticado")
            
            if not parque.esta_abierto(fecha_visita):
                raise ValidationError("La fecha seleccionada no está disponible en el parque")
            
            if cantidad < 1 or cantidad > 10:
                raise ValidationError("La cantidad debe ser entre 1 y 10 entradas")
            
            if not edades_visitantes or len(edades_visitantes) != cantidad:
                raise ValidationError("La cantidad de entradas debe coincidir con el número de edades")
            
            for edad in edades_visitantes:
                if not isinstance(edad, int) or edad < 0 or edad > 120:
                    raise ValidationError("Las edades deben estar entre 0 y 120 años")
            
            if forma_pago not in ['efectivo', 'tarjeta']:
                raise ValidationError("Debe seleccionar una forma de pago válida")
            
            # Crear compra
            compra = Compra.objects.create(
                usuario=visitante,
                parque=parque
            )
            
            # Crear entradas individuales
            monto_total = 0
            for edad in edades_visitantes:
                tipo_pase_int = Entrada.VIP if tipo_pase.upper() == 'VIP' else Entrada.REGULAR
                entrada = Entrada.objects.create(
                    fecha_visita=fecha_visita,
                    tipo_pase=tipo_pase_int,
                    edad_visitante=edad,
                    precio=0,  # Se calcula automáticamente en save()
                    compra=compra
                )
                monto_total += entrada.precio
            
            # Actualizar monto total de la compra
            compra.monto_total = monto_total
            compra.save()
            
            # Convertir forma de pago a constante
            forma_pago_int = Pago.EFECTIVO if forma_pago == 'efectivo' else Pago.TARJETA
            
            # Usar el servicio para procesar
            resultado = self.comprar(compra, forma_pago_int)
            
            # Adaptar respuesta al formato esperado por los tests
            if resultado['success']:
                # Para compatibilidad, devolvemos la primera entrada con propiedades de compatibilidad
                primera_entrada = compra.entradas.first()
                # Agregar propiedades de compatibilidad dinámicamente
                primera_entrada.tipo_pase = primera_entrada.tipo_pase_display
                return {
                    'success': True,
                    'entrada': primera_entrada,
                    'pago': resultado['pago'],
                    'email_enviado': resultado['email_enviado'],
                    'redirect_to_mercadopago': resultado['redirect_to_mercadopago'],
                    'transaction_id': resultado['transaction_id']
                }
            else:
                return resultado
                
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'entrada': None,
                'pago': None
            }
        except Exception as e:
            logger.error(f"Error inesperado en proceso de compra: {str(e)}")
            return {
                'success': False,
                'error': 'Error interno del servidor',
                'entrada': None,
                'pago': None
            }
    
    def obtener_resumen_compra(self, entrada):
        """Método de compatibilidad para obtener resumen de compra"""
        compra = entrada.compra if hasattr(entrada, 'compra') else None
        if compra:
            return {
                'cantidad_entradas': compra.entradas.count(),
                'fecha_visita': entrada.fecha_visita,
                'tipo_pase': entrada.tipo_pase_display,
                'monto_total': compra.monto_total,
                'forma_pago': 'tarjeta',  # Por simplicidad
                'fecha_compra': compra.fecha_compra
            }
        else:
            # Fallback para compatibilidad
            return {
                'cantidad_entradas': 1,
                'fecha_visita': entrada.fecha_visita,
                'tipo_pase': 'VIP' if entrada.tipo_pase == Entrada.VIP else 'Regular',
                'monto_total': entrada.precio,
                'forma_pago': 'efectivo',
                'fecha_compra': entrada.fecha_visita  # Fallback
            }
    
    def validar_edades_visitantes(self, edades_visitantes, cantidad):
        """
        Método de compatibilidad para validar edades de visitantes
        
        Args:
            edades_visitantes: Lista de edades
            cantidad: Cantidad esperada de visitantes
            
        Raises:
            ValidationError: Si las validaciones fallan
        """
        if not edades_visitantes:
            raise ValidationError("Debe proporcionar las edades de todos los visitantes")
        
        if len(edades_visitantes) != cantidad:
            raise ValidationError("La cantidad de entradas debe coincidir con el número de edades")
        
        for edad in edades_visitantes:
            if not isinstance(edad, int) or edad < 0 or edad > 120:
                raise ValidationError("Las edades deben estar entre 0 y 120 años")
        
        return True
            
