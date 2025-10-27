from django import forms
from django.core.exceptions import ValidationError
import datetime

# Importar los feriados del nuevo archivo
from .constants import FERIADOS

class ComprarEntradasForm(forms.Form):
    # Datos del usuario (simulado como campos del form)
    usuario_nombre = forms.CharField(
        max_length=100, 
        label="Nombre del usuario",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    usuario_email = forms.EmailField(
        label="Email del usuario",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    # Fecha de visita
    fecha_visita = forms.DateField(
        label="Fecha de visita",
        widget=forms.DateInput(attrs={
            'class': 'form-control', 
            'type': 'date',
            'min': datetime.date.today().strftime('%Y-%m-%d')
        })
    )
    
    def clean_fecha_visita(self):
        fecha = self.cleaned_data['fecha_visita']
        
        # Validar que no sea una fecha pasada
        if fecha < datetime.date.today():
            raise ValidationError("No se pueden comprar entradas para fechas pasadas.")
        
        # Validar que no sea lunes
        if fecha.weekday() == 0:
            raise ValidationError("El parque está cerrado los lunes.")
        
        # Validar que no sea feriado
        if fecha in FERIADOS:
            raise ValidationError("El parque está cerrado en feriados.")
        
        return fecha
    
    # Tipo de pase
    TIPO_PASE_CHOICES = [
        ('REGULAR', 'Pase Regular'),
        ('VIP', 'Pase VIP'),
    ]
    tipo_pase = forms.ChoiceField(
        choices=TIPO_PASE_CHOICES,
        label="Tipo de pase",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Forma de pago
    FORMA_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
    ]
    forma_pago = forms.ChoiceField(
        choices=FORMA_PAGO_CHOICES,
        label="Forma de pago",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Cantidad de visitantes
    cantidad_visitantes = forms.IntegerField(
    min_value=1,
    max_value=10,
    label="Cantidad de visitantes",
    widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'id': 'cantidad_visitantes',
            # Permitir teclado numérico en móviles y aceptar teclas comunes de navegación
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'min': '1',
            'max': '10',
            # onkeydown más permisivo: permite dígitos, teclas de navegación y acepta 'Unidentified' (teclados virtuales móviles)
            'onkeydown': "if(!(event.key.length === 1 && /\\d/.test(event.key)) && !['ArrowUp','ArrowDown','Tab','Backspace','Delete','ArrowLeft','ArrowRight','Home','End'].includes(event.key) && event.key !== 'Unidentified') event.preventDefault();"
        }
    )
    )

class VisitanteForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    edad = forms.IntegerField(
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )