from domain.Estudiante import Estudiante

class Lote:
    def __init__(
            self,
            fecha,
            prueba,
            grado,
            jornada,
            sesion,
            estudiantes
    ):
        
        if not isinstance(fecha, str):
            raise TypeError("La fecha debe ser un string")
        
        if fecha.strip() == "":
            raise ValueError("La fecha no puede estar vacía")
        
        if not isinstance(prueba, str):
            raise TypeError("La prueba debe ser un string")
        
        if prueba.strip() == "":
            raise ValueError("La prueba no puede estar vacía")
        
        if not isinstance(grado, str):
            raise TypeError("El grado debe ser un string")
        
        if grado.strip() not in ["10", "11"]:
            raise ValueError("El grado debe ser 10 o 11")
        
        if not isinstance(jornada, str):
            raise TypeError("La jornada debe ser un string")
        
        jornada_normalizada = jornada.strip().capitalize()
        
        if jornada_normalizada not in ["Mañana" , "Tarde"]:
            raise ValueError("La jornada debe ser 'Mañana' o 'Tarde'")
        
        if not isinstance(sesion, str):
            raise TypeError("La sesion debe ser un string")
        
        if sesion.strip() not in ["1", "2"]:
            raise ValueError("La sesion debe ser '1' o '2'")
        
        if not isinstance(estudiantes, list):
            raise TypeError("Estudiantes debe ser una lista")
        
        for estudiante in estudiantes:
            if not isinstance(estudiante, Estudiante):
                raise TypeError("Cada elemento de estudiantes debe ser una instancia de Estudiante")                   
        
        self.fecha = fecha.strip() #el strip sirve para eliminar espacios en blanco al inicio y al final
        self.prueba = prueba.strip() 
        self.grado = grado.strip() 
        self.jornada = jornada_normalizada 
        self.sesion = sesion.strip() 
        self.estudiantes = estudiantes
