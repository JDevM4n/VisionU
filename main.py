from domain.Estudiante import Estudiante
from domain.Lote import Lote
from infrastructure.excel_reader import agregar_estudiantes
from datetime import datetime

fecha = datetime.now().strftime("%d/%m/%Y")
prueba = "Prueba"
grado = "10"
jornada = "tarde"
sesion = "1"
estudiantes = agregar_estudiantes("inputs\\estudiantes.xlsx", "PU3")

lote = Lote(
    fecha,
    prueba,
    grado,
    jornada,
    sesion,
    estudiantes
)
