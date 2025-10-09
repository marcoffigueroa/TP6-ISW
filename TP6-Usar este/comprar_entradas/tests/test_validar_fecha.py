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


def test_validar_fecha_visita_con_parque_cerrado():
    hoy = date.today()

    # Buscamos la próxima fecha cerrada (lunes o feriado)
    fecha_cerrada = hoy
    while fecha_cerrada.weekday() != 0 and fecha_cerrada not in FERIADOS:
        fecha_cerrada += timedelta(days=1)

    # Debe lanzar ValueError porque la fecha está cerrada
    with pytest.raises(ValueError) as excinfo:
        validar_fecha_visita(fecha_cerrada, feriados=FERIADOS)

    # Verificamos que el mensaje contenga "cerrado"
    assert "cerrado" in str(excinfo.value).lower()
