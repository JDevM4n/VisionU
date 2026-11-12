from openpyxl import load_workbook

from domain.Estudiante import Estudiante


# =========================================================
# NORMALIZAR NOMBRE DE HOJA
# =========================================================

def normalizar_nombre_hoja(nombre):

    return (
        str(nombre)
        .strip()
        .casefold()
    )


# =========================================================
# BUSCAR HOJA
# =========================================================

def encontrar_hoja(
    workbook,
    nombre_solicitado
):

    nombre_normalizado = (
        normalizar_nombre_hoja(
            nombre_solicitado
        )
    )

    for nombre_real in workbook.sheetnames:

        if (
            normalizar_nombre_hoja(
                nombre_real
            )
            ==
            nombre_normalizado
        ):

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

def encontrar_fila_encabezado(
    hoja
):

    for numero_fila, filas in enumerate(
        hoja.iter_rows(),
        start=1
    ):

        for celda in filas:

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


            if "DOCUMENTO" in texto:

                return numero_fila


    raise ValueError(
        "No se pudo encontrar la fila "
        "de encabezados del Excel."
    )


# =========================================================
# NORMALIZAR ENCABEZADO
# =========================================================

def normalizar_encabezado(
    valor
):

    if valor is None:
        return ""


    return (
        str(valor)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
        .upper()
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

        texto = normalizar_encabezado(
            celda.value
        )


        if texto == "":
            continue


        # ==========================================
        # DOCUMENTO
        # ==========================================

        if (
            "DOCUMENTO" in texto
            and
            "documento" not in columnas
        ):

            columnas[
                "documento"
            ] = indice


        # ==========================================
        # NOMBRE
        # ==========================================

        elif (
            "NOMBRE COMPLETO ESTUDIANTE"
            in texto
            or
            "NOMBRE COMPLETO"
            in texto
            or
            texto == "NOMBRE"
        ):

            if "nombre" not in columnas:

                columnas[
                    "nombre"
                ] = indice


        # ==========================================
        # COLEGIO
        # ==========================================

        elif texto == "COLEGIO":

            columnas[
                "colegio"
            ] = indice


        # ==========================================
        # GRUPO
        # ==========================================

        elif texto == "GRUPO":

            columnas[
                "grupo"
            ] = indice


        # ==========================================
        # MUNICIPIO / CIUDAD
        # ==========================================

        elif (
            texto == "MUNICIPIO"
            or
            texto == "CIUDAD"
        ):

            columnas[
                "ciudad"
            ] = indice


    # ==========================================
    # IMPORTANTÍSIMO:
    # GRADO YA NO ES OBLIGATORIO EN EL EXCEL
    # ==========================================

    campos_obligatorios = [
        "documento",
        "nombre",
        "colegio",
        "grupo",
        "ciudad",
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


# =========================================================
# LIMPIAR TEXTO
# =========================================================

def limpiar_texto(
    valor
):

    if valor is None:
        return ""


    return (
        str(valor)
        .strip()
    )


# =========================================================
# LIMPIAR DOCUMENTO
# =========================================================

def limpiar_documento(
    valor
):

    if valor is None:
        return ""


    # Excel puede devolver algunos números
    # como float: 1097784968.0

    if isinstance(
        valor,
        float
    ):

        if valor.is_integer():

            return str(
                int(valor)
            )


    return (
        str(valor)
        .strip()
    )


# =========================================================
# AGREGAR ESTUDIANTES
# =========================================================

def agregar_estudiantes(
    ruta_archivo,
    nombre_hoja,
    grado
):

    workbook = load_workbook(
        ruta_archivo,
        data_only=True
    )


    try:

        # ==========================================
        # ENCONTRAR HOJA
        # ==========================================

        nombre_real = encontrar_hoja(
            workbook,
            nombre_hoja
        )


        print(
            "Hoja solicitada:",
            repr(nombre_hoja)
        )


        print(
            "Hoja encontrada:",
            repr(nombre_real)
        )


        hoja = workbook[
            nombre_real
        ]


        # ==========================================
        # ENCONTRAR ENCABEZADOS
        # ==========================================

        fila_encabezado = (
            encontrar_fila_encabezado(
                hoja
            )
        )


        print(
            "Fila de encabezados:",
            fila_encabezado
        )


        columnas = obtener_columnas(
            hoja,
            fila_encabezado
        )


        estudiantes = []


        # ==========================================
        # RECORRER FILAS
        # ==========================================

        for fila in hoja.iter_rows(
            min_row=
                fila_encabezado + 1
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


            ciudad = fila[
                columnas["ciudad"]
            ].value


            # ======================================
            # OMITIR FILAS VACÍAS
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

            documento = limpiar_documento(
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


            ciudad = limpiar_texto(
                ciudad
            )


            grado_estudiante = (
                limpiar_texto(
                    grado
                )
            )


            # ======================================
            # CREAR ESTUDIANTE
            # ======================================

            estudiante = Estudiante(
                documento,
                nombre,
                colegio,
                grupo,
                grado_estudiante,
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