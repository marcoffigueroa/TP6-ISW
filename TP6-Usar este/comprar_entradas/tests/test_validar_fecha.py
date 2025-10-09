import pytest
from datetime import date, timedelta
from comprar_entradas.views import validar_fecha_visita
# Feriados hardcodeados (solo ejemplo)
FERIADOS = [
    date(2025, 12, 25),  # Navidad
    date(2025, 1, 1),    # Año Nuevo
]

def test_validar_fecha_visita_abierta():
    hoy = date.today()

    # Buscamos el próximo día hábil que no sea lunes y no esté en feriados
    fecha_valida = hoy
    while fecha_valida.weekday() == 0 or fecha_valida in FERIADOS:
        fecha_valida += timedelta(days=1)

    # Ejecutamos la validación
    resultado = validar_fecha_visita(fecha_valida, feriados=FERIADOS)

    # La función debe devolver True si la fecha es válida
    assert resultado is True
