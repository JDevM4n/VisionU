from openpyxl import load_workbook
from domain.Estudiante import Estudiante

def encontrar_fila_encabezado(hoja): #funcion para encontrar en que fila se encuentran los encabezados
    for numero_fila, filas in enumerate(hoja.iter_rows(), start=1):
        for celda in filas:
            if isinstance(celda.value, str):
                texto = celda.value.strip().upper()

                if "DOCUMENTO" in texto:
                    return numero_fila
                

def obtener_columnas(hoja, fila_encabezado):

    columnas = {}

    for indice, celda in enumerate(
        hoja[fila_encabezado]
    ):

        if not isinstance(
            celda.value,
            str
        ):
            continue


        texto = (
            celda.value
            .strip()
            .upper()
        )


        # ==========================================
        # DOCUMENTO
        # ==========================================

        if (
            "DOCUMENTO" in texto
            and
            "documento" not in columnas
        ):
            columnas["documento"] = indice


        # ==========================================
        # NOMBRE
        # ==========================================

        elif (
            "NOMBRE COMPLETO" in texto
            and
            "nombre" not in columnas
        ):
            columnas["nombre"] = indice


        elif (
            texto == "NOMBRE"
            and
            "nombre" not in columnas
        ):
            columnas["nombre"] = indice


        # ==========================================
        # COLEGIO
        # ==========================================

        elif (
            "COLEGIO" in texto
            and
            "colegio" not in columnas
        ):
            columnas["colegio"] = indice


        # ==========================================
        # GRUPO
        # AQUÍ ESTÁ EL CAMBIO IMPORTANTE
        # ==========================================

        elif texto == "GRUPO":

            columnas["grupo"] = indice


        # ==========================================
        # GRADO / CURSO
        # ==========================================

        elif texto == "CURSO":

            columnas["grado"] = indice


        elif texto == "GRADO":

            columnas["grado"] = indice


        # ==========================================
        # CIUDAD
        # ==========================================

        elif (
            texto == "MUNICIPIO"
            or
            texto == "CIUDAD"
        ):

            columnas["ciudad"] = indice


    # ==========================================
    # VERIFICAR QUE ESTÉ TODO
    # ==========================================

    campos_obligatorios = [

        "documento",
        "nombre",
        "colegio",
        "grupo",
        "grado",
        "ciudad"

    ]


    faltantes = [

        campo

        for campo
        in campos_obligatorios

        if campo not in columnas

    ]


    if faltantes:

        raise ValueError(

            "No se encontraron estas columnas: "

            + ", ".join(
                faltantes
            )

        )


    print(
        "Columnas detectadas:",
        columnas
    )


    return columnas




def agregar_estudiantes(ruta_archivo, nombre_hoja): #funcion para agregar estudiantes 
    workbook = load_workbook(ruta_archivo)
    hoja = workbook[nombre_hoja]
    
    fila_encabezado = encontrar_fila_encabezado(hoja)
    columnas = obtener_columnas(hoja, fila_encabezado)
    estudiantes = []
    
    for fila in hoja.iter_rows(min_row=fila_encabezado + 1):
        
        
        documento = fila[columnas["documento"]].value
        nombre = fila[columnas["nombre"]].value
        colegio = fila[columnas["colegio"]].value
        grupo = fila[columnas["grupo"]].value
        grado = fila[columnas["grado"]].value
        ciudad = fila[columnas["ciudad"]].value
        
        if documento is None or nombre is None:
            continue
        
        documento = str(documento)
        nombre = str(nombre)
        colegio = str(colegio)
        grupo = str(grupo)
        grado = grado.replace("°", "").split()[-1]
        ciudad = str(ciudad)
        
        
        estudiante = Estudiante(
            documento,
            nombre,
            colegio,
            grupo,
            grado,
            ciudad
        )
        
        estudiantes.append(estudiante)
    return estudiantes