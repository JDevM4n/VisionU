from openpyxl import load_workbook
from domain.Estudiante import Estudiante


# =========================================================
# NORMALIZAR NOMBRE DE HOJA
# =========================================================

def normalizar_nombre_hoja(nombre):
    """
    Normaliza el nombre de una hoja para poder comparar
    ignorando espacios al inicio/final y mayúsculas/minúsculas.
    """

    return str(nombre).strip().casefold()


# =========================================================
# ENCONTRAR HOJA DEL EXCEL
# =========================================================

def encontrar_hoja(
    workbook,
    nombre_solicitado
):
    """
    Busca una hoja de Excel sin depender de coincidencia
    exacta de mayúsculas/minúsculas o espacios sobrantes.
    """

    nombre_normalizado = normalizar_nombre_hoja(
        nombre_solicitado
    )

    for nombre_real in workbook.sheetnames:

        if normalizar_nombre_hoja(
            nombre_real
        ) == nombre_normalizado:

            return nombre_real

    disponibles = ", ".join(
        workbook.sheetnames
    )

    raise ValueError(
        f"No existe la hoja '{nombre_solicitado}'. "
        f"Hojas disponibles: {disponibles}"
    )


# =========================================================
# ENCONTRAR FILA DE ENCABEZADOS
# =========================================================

def encontrar_fila_encabezado(hoja):
    """
    Encuentra la fila donde se encuentran los encabezados
    buscando una celda que contenga la palabra DOCUMENTO.
    """

    for numero_fila, filas in enumerate(
        hoja.iter_rows(),
        start=1
    ):

        for celda in filas:

            if isinstance(
                celda.value,
                str
            ):

                texto = (
                    celda.value
                    .strip()
                    .upper()
                )

                if "DOCUMENTO" in texto:

                    return numero_fila

    raise ValueError(
        "No se pudo encontrar la fila de encabezados. "
        "Debe existir una columna que contenga "
        "la palabra 'DOCUMENTO'."
    )


# =========================================================
# DETECTAR COLUMNAS
# =========================================================

def obtener_columnas(
    hoja,
    fila_encabezado
):

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
    # VERIFICAR CAMPOS OBLIGATORIOS
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

        for campo in campos_obligatorios

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


# =========================================================
# LIMPIAR VALOR
# =========================================================

def limpiar_texto(valor):
    """
    Convierte valores del Excel a texto de forma segura.
    """

    if valor is None:
        return ""

    return str(valor).strip()


# =========================================================
# NORMALIZAR GRADO
# =========================================================

def normalizar_grado(valor):
    """
    Convierte valores como:
    10
    10°
    Grado 10
    Curso 10

    en:
    10
    """

    texto = limpiar_texto(
        valor
    )

    texto = texto.replace(
        "°",
        ""
    )

    if not texto:

        return ""

    return texto.split()[-1]


# =========================================================
# AGREGAR ESTUDIANTES
# =========================================================

def agregar_estudiantes(
    ruta_archivo,
    nombre_hoja
):

    # ==============================================
    # ABRIR EXCEL
    # ==============================================

    workbook = load_workbook(
        ruta_archivo,
        data_only=True
    )


    try:

        # ==========================================
        # BUSCAR NOMBRE REAL DE LA HOJA
        # ==========================================

        nombre_real_hoja = encontrar_hoja(
            workbook,
            nombre_hoja
        )


        print(
            f"Hoja solicitada: '{nombre_hoja}'"
        )

        print(
            f"Hoja encontrada: '{nombre_real_hoja}'"
        )


        hoja = workbook[
            nombre_real_hoja
        ]


        # ==========================================
        # ENCONTRAR ENCABEZADOS
        # ==========================================

        fila_encabezado = (
            encontrar_fila_encabezado(
                hoja
            )
        )


        columnas = obtener_columnas(
            hoja,
            fila_encabezado
        )


        estudiantes = []


        # ==========================================
        # LEER ESTUDIANTES
        # ==========================================

        for fila in hoja.iter_rows(
            min_row=fila_encabezado + 1
        ):

            documento = fila[
                columnas["documento"]
            ].value

            nombre = fila[
                columnas["nombre"]
            ].value

            colegio = fila[
                columnas["colegio"]
            ].value

            grupo = fila[
                columnas["grupo"]
            ].value

            grado = fila[
                columnas["grado"]
            ].value

            ciudad = fila[
                columnas["ciudad"]
            ].value


            # ======================================
            # FILAS VACÍAS
            # ======================================

            if (
                documento is None
                or
                nombre is None
            ):

                continue


            # ======================================
            # NORMALIZAR DATOS
            # ======================================

            documento = limpiar_texto(
                documento
            )

            nombre = limpiar_texto(
                nombre
            )

            colegio = limpiar_texto(
                colegio
            )

            grupo = limpiar_texto(
                grupo
            )

            grado = normalizar_grado(
                grado
            )

            ciudad = limpiar_texto(
                ciudad
            )


            # ======================================
            # CREAR ESTUDIANTE
            # ======================================

            estudiante = Estudiante(
                documento,
                nombre,
                colegio,
                grupo,
                grado,
                ciudad
            )


            estudiantes.append(
                estudiante
            )


        print(
            "Estudiantes encontrados:",
            len(estudiantes)
        )


        return estudiantes


    finally:

        workbook.close()