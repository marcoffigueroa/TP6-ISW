from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from datetime import date, datetime
import re


class Usuario(AbstractUser):
    """
    Clase Usuario - Representa a un visitante registrado que puede realizar compras
    
    Atributos:
    - idUsuario: int (inherited as pk)
    - nombre: str (mapped to username)
    - email: str
    - password: str (inherited)
    
    Relación: 1..1 con Compra
    """
    # idUsuario se maneja automáticamente como primary key
    # nombre se mapea a username (inherited)
    email = models.EmailField(unique=True)
    # password se hereda de AbstractUser
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def login(self, email: str, password: str):
        """Método para autenticar usuario"""
        user = authenticate(username=email, password=password)
        return user is not None
    
    def registrarse(self):
        """Método para validar registro del usuario"""
        if not self.email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
            raise ValidationError("Email inválido")
        if len(self.password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        return True
    
    def __str__(self):
        return f"{self.username} ({self.email})"


class Parque(models.Model):
    """
    Clase Parque - Define los días de apertura y cierre del bioparque
    
    Atributos:
    - diasAbiertos: list[str]
    - diasCerradosEspeciales: list[str]
    
    Relación: Compra depende de Parque para validar disponibilidad
    """
    nombre = models.CharField(max_length=100, default="Parque Principal")
    dias_abiertos = models.JSONField(default=list)  # Lista de días de la semana (0=lunes, 6=domingo)
    dias_cerrados_especiales = models.JSONField(default=list)  # Fechas específicas cerradas
    
    def esta_abierto(self, fecha: date) -> bool:
        """
        Método para verificar si el parque está abierto en una fecha específica
        
        Args:
            fecha: Fecha a verificar
            
        Returns:
            bool: True si está abierto, False si está cerrado
        """
        if not isinstance(fecha, date):
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                except ValueError:
                    return False
            else:
                return False
        
        # Verificar que no sea una fecha pasada
        if fecha < date.today():
            return False
            
        # Verificar días cerrados especiales
        fecha_str = fecha.strftime('%Y-%m-%d')
        if fecha_str in self.dias_cerrados_especiales:
            return False
            
        # Verificar día de la semana (0=lunes, 6=domingo)
        dia_semana = fecha.weekday()
        return dia_semana in self.dias_abiertos
    
    def __str__(self):
        return self.nombre


class Compra(models.Model):
    """
    Clase Compra - Entidad principal del proceso de compra
    
    Atributos:
    - idCompra: int (auto primary key)
    - fechaCompra: date
    - usuario: Usuario
    - entradas: list[Entrada] (reverse foreign key)
    - pago: Pago (one-to-one)
    - parque: Parque
    - montoTotal: float
    
    Rol: Coordina usuario, entradas, parque y servicios de pago/notificación
    """
    # idCompra se maneja automáticamente como primary key
    fecha_compra = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras')
    # entradas se accede via reverse foreign key
    parque = models.ForeignKey(Parque, on_delete=models.CASCADE)
    monto_total = models.FloatField(default=0.0)
    
    def calcular_monto_total(self) -> float:
        """
        Calcula el monto total de todas las entradas de esta compra
        
        Returns:
            float: Monto total calculado
        """
        total = sum(entrada.precio for entrada in self.entradas.all())
        self.monto_total = total
        return total
    
    def __str__(self):
        return f"Compra {self.id} - {self.usuario.username} - ${self.monto_total}"


class Entrada(models.Model):
    """
    Clase Entrada - Representa una entrada individual
    
    Atributos:
    - idEntrada: int (auto primary key)  
    - fechaVisita: date
    - tipoPase: int (1 = regular, 2 = VIP)
    - edadVisitante: int
    - precio: float
    
    Relación: una Compra puede tener una o más Entrada (1..*)
    """
    
    # Constantes para tipos de pase
    REGULAR = 1
    VIP = 2
    
    TIPO_PASE_CHOICES = [
        (REGULAR, 'Regular'),
        (VIP, 'VIP'),
    ]
    
    # Precios base
    PRECIO_REGULAR = 1000.0
    PRECIO_VIP = 2500.0
    
    # idEntrada se maneja automáticamente como primary key
    fecha_visita = models.DateField()
    tipo_pase = models.IntegerField(choices=TIPO_PASE_CHOICES, default=REGULAR)
    edad_visitante = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)]
    )
    precio = models.FloatField()
    
    # Relación con Compra
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='entradas')
    
    def save(self, *args, **kwargs):
        """Override save para calcular precio automáticamente"""
        if not self.precio:
            if self.tipo_pase == self.VIP:
                self.precio = self.PRECIO_VIP
            else:
                self.precio = self.PRECIO_REGULAR
        super().save(*args, **kwargs)
    
    # Propiedades de compatibilidad para tests antiguos
    @property
    def cantidad(self):
        """Compatibilidad: retorna la cantidad total de entradas en la compra"""
        return self.compra.entradas.count()
    
    @property
    def edades_visitantes(self):
        """Compatibilidad: retorna lista de edades de todas las entradas en la compra"""
        return list(self.compra.entradas.values_list('edad_visitante', flat=True))
    
    @property
    def forma_pago(self):
        """Compatibilidad: retorna la forma de pago como string"""
        try:
            pago = self.compra.pago
            return 'efectivo' if pago.forma_de_pago == Pago.EFECTIVO else 'tarjeta'
        except:
            return None

    @property
    def tipo_pase_display(self):
        """Compatibilidad: retorna el tipo de pase como string"""
        if self.tipo_pase == self.VIP or self.tipo_pase == 'VIP':
            return 'VIP'
        else:
            return 'Regular'

    def __str__(self):
        tipo_str = "VIP" if self.tipo_pase == self.VIP else "Regular"
        return f"Entrada {tipo_str} - {self.fecha_visita} - Edad {self.edad_visitante}"


class Pago(models.Model):
    """
    Clase Pago - Representa el pago asociado a una compra
    
    Atributos según IPaymentService:
    - idPago: int (auto primary key)
    - formaDePago: int (1 = efectivo, 2 = tarjeta)
    - estado: int
    - monto: float
    - idTransaccionExterna: str
    """
    
    # Constantes para formas de pago
    EFECTIVO = 1
    TARJETA = 2
    
    FORMA_PAGO_CHOICES = [
        (EFECTIVO, 'Efectivo'),
        (TARJETA, 'Tarjeta'),
    ]
    
    # Estados de pago
    PENDIENTE = 1
    PROCESADO = 2
    FALLIDO = 3
    
    ESTADO_CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (PROCESADO, 'Procesado'),
        (FALLIDO, 'Fallido'),
    ]
    
    # idPago se maneja automáticamente como primary key
    forma_de_pago = models.IntegerField(choices=FORMA_PAGO_CHOICES)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=PENDIENTE)
    monto = models.FloatField()
    id_transaccion_externa = models.CharField(max_length=255, blank=True, null=True)
    
    # Relación one-to-one con Compra
    compra = models.OneToOneField(Compra, on_delete=models.CASCADE, related_name='pago')
    
    def __str__(self):
        estado_str = dict(self.ESTADO_CHOICES)[self.estado]
        forma_str = dict(self.FORMA_PAGO_CHOICES)[self.forma_de_pago]
        return f"Pago {forma_str} - ${self.monto} - {estado_str}"
