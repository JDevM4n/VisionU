class Estudiante:
    def __init__(
            self,
            documento,
            nombre,
            colegio,
            grupo,
            grado,
            ciudad
    ):
        if not isinstance(documento, str):
            raise TypeError("El documento debe ser un string")
        
        if documento.strip() == "":
            raise ValueError("El documento no puede estar vacío")
        
        if not isinstance(nombre, str):
            raise TypeError("El nombre debe ser un string")
        
        if nombre.strip() == "":
            raise ValueError("El nombre no puede estar vacío")
        
        if not isinstance(colegio, str):
            raise TypeError("El colegio debe ser un string")
        
        if colegio.strip() == "":
            raise ValueError("El colegio no puede estar vacío")
        
        if not isinstance(grupo,str):
            raise TypeError("El grupo debe ser un string")
        
        if grupo.strip() == "":
            raise ValueError("El grupo no puede estar vacío")
        
        if not isinstance(grado, str):
            raise TypeError("El grado debe ser un string")
        
        if grado.strip() not in ["10", "11"]:
            raise ValueError("El grado debe ser 10 o 11")
        
        if not isinstance(ciudad, str):
            raise TypeError("La ciudad debe ser un string")
        
        if ciudad.strip() == "":
            raise ValueError("La ciudad no puede estar vacía")
        
        self.documento = documento
        self.nombre = nombre
        self.colegio = colegio
        self.grupo = grupo
        self.grado = grado
        self.ciudad = ciudad