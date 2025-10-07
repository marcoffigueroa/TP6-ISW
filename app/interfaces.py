from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IPaymentService(ABC):
    """Interfaz para servicios de pago"""
    
    def __init__(self):
        self.id_pago: int = None
        self.forma_de_pago: int = None  # 1 = efectivo, 2 = tarjeta
        self.estado: int = None
        self.monto: float = None
        self.id_transaccion_externa: str = None
    
    @abstractmethod
    def procesar_pago(self, monto: float, forma_pago: int) -> Dict[str, Any]:
        """
        Procesa el pago según la forma especificada
        
        Args:
            monto: Monto total a procesar
            forma_pago: 1 = efectivo, 2 = tarjeta
            
        Returns:
            Dict con resultado del procesamiento
        """
        pass


class INotificacionService(ABC):
    """Interfaz para servicios de notificación"""
    
    @abstractmethod
    def enviar_confirmacion(self, usuario, compra) -> bool:
        """
        Envía confirmación al usuario tras una compra exitosa
        
        Args:
            usuario: Instancia del usuario
            compra: Instancia de la compra realizada
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        pass