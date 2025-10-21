import pytest

def test_validar_datos_visitantes_correctos():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import validar_datos_visitantes
    except ImportError:
        pytest.fail("La función 'validar_datos_visitantes' no está definida o no se puede importar")

    # Arrange
    visitantes = [
        {"nombre": "Ana", "edad": 25},
        {"nombre": "Luis", "edad": 30},
        {"nombre": "Marta", "edad": 12},
    ]

    # Act
    resultado = validar_datos_visitantes(visitantes)

    # Assert
    # Si la función existe, debería devolver True o no lanzar excepción
    assert resultado is True or resultado is None

def test_validar_datos_visitantes_faltantes():
    # Verificamos que la función exista
    try:
        from comprar_entradas.views import validar_datos_visitantes
    except ImportError:
        pytest.fail("La función 'validar_datos_visitantes' no está definida o no se puede importar")

    # Arrange: visitantes con datos faltantes (uno sin edad)
    visitantes = [
        {"edad": 25},
        {"nombre": "Luis"},  # Falta la edad
        {"nombre": "Marta", "edad": 12},
    ]

    # Act & Assert: esperamos que falle o lance excepción
    with pytest.raises(Exception):
        validar_datos_visitantes(visitantes)