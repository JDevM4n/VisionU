from domain.Estudiante import Estudiante
from domain.Lote import Lote

try:
    estudiante = Estudiante(
        "12345678",
        "Juan Perez",
        "Colegio Nacional",
        "A",
        "10",
        "Bogota"
    )

except ValueError as e:
    print(f"Error de valor: {e}")

except TypeError as e:
    print(f"Error de tipo: {e}")
    

lote = Lote(
    "2024-06-05",
    "Matematicas",
    "10",
    "Mañana",
    "1",
    []
)

lote.agregar_estudiante(estudiante)