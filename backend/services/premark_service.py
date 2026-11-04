import pymupdf

from infrastructure.pdf_writer import (
    aplicar_guias,
    mm_a_pt,
)

from infrastructure.qr_generator import (
    generar_qr_bytes,
)


# =========================================================
# CONFIGURACIÓN QR
# =========================================================

QR_TAMANO_MM = 30
QR_X_MM = 175
QR_Y_MM = 47


# =========================================================
# CONFIGURACIÓN DEL ENCABEZADO
# =========================================================

FUENTE = "helv"

TAMANO_MAXIMO = 12
TAMANO_MINIMO = 10


# =========================================================
# DISTANCIA DESDE EL INICIO DE CADA CAMPO
# =========================================================

OFFSET_CAMPOS_MM = {
    "fecha": 14,
    "documento": 45,
    "nombre": 16,
    "colegio": 16,
    "evaluacion": 22,
    "grupo": 15,
    "grado": 15,
    "sesion": 14,
    "contador": 2,
    "ciudad": 14,
}


# =========================================================
# INSERTAR QR
# =========================================================

def insertar_qr(
    pagina,
    estudiante,
    lote,
    numero_estudiante,
    total_estudiantes,
):

    qr_bytes, contenido = generar_qr_bytes(
        estudiante,
        lote,
        numero_estudiante,
        total_estudiantes,
    )

    tamano = mm_a_pt(
        QR_TAMANO_MM
    )

    x = mm_a_pt(
        QR_X_MM
    )

    y = mm_a_pt(
        QR_Y_MM
    )

    rectangulo_qr = pymupdf.Rect(
        x,
        y,
        x + tamano,
        y + tamano,
    )

    pagina.insert_image(
        rectangulo_qr,
        stream=qr_bytes,
    )

    print(
        "QR:",
        contenido,
    )


# =========================================================
# COMPARAR RECTÁNGULOS
# =========================================================

def rectangulos_similares(
    rectangulo_1,
    rectangulo_2,
    tolerancia=1.5,
):

    return (
        abs(
            rectangulo_1.x0
            - rectangulo_2.x0
        ) <= tolerancia

        and

        abs(
            rectangulo_1.y0
            - rectangulo_2.y0
        ) <= tolerancia

        and

        abs(
            rectangulo_1.x1
            - rectangulo_2.x1
        ) <= tolerancia

        and

        abs(
            rectangulo_1.y1
            - rectangulo_2.y1
        ) <= tolerancia
    )


# =========================================================
# ELIMINAR RECTÁNGULOS DUPLICADOS
# =========================================================

def eliminar_duplicados(
    rectangulos,
):

    resultado = []

    for rectangulo in rectangulos:

        duplicado = False

        for existente in resultado:

            if rectangulos_similares(
                rectangulo,
                existente,
            ):

                duplicado = True
                break

        if not duplicado:

            resultado.append(
                rectangulo
            )

    return resultado


# =========================================================
# AGRUPAR RECTÁNGULOS POR FILAS
# =========================================================

def agrupar_por_filas(
    rectangulos,
    tolerancia=3,
):

    rectangulos = sorted(
        rectangulos,
        key=lambda rectangulo: (
            rectangulo.y0,
            rectangulo.x0,
        ),
    )

    filas = []

    for rectangulo in rectangulos:

        encontrado = False

        for fila in filas:

            promedio_y = sum(
                elemento.y0
                for elemento in fila
            ) / len(fila)

            if abs(
                rectangulo.y0
                - promedio_y
            ) <= tolerancia:

                fila.append(
                    rectangulo
                )

                encontrado = True
                break

        if not encontrado:

            filas.append(
                [rectangulo]
            )

    filas.sort(
        key=lambda fila:
        sum(
            rectangulo.y0
            for rectangulo in fila
        ) / len(fila)
    )

    for fila in filas:

        fila.sort(
            key=lambda rectangulo:
            rectangulo.x0
        )

    return filas


# =========================================================
# DETECTAR CAMPOS DEL ENCABEZADO
# =========================================================

def detectar_campos_encabezado(
    pagina,
):

    candidatos = []

    # Solo analizamos aproximadamente
    # el 25 % superior de la página.
    limite_encabezado = (
        pagina.rect.height * 0.25
    )

    for dibujo in pagina.get_drawings():

        rectangulo = dibujo["rect"]

        # ---------------------------------------------
        # Debe estar en la parte superior
        # ---------------------------------------------

        if rectangulo.y1 > limite_encabezado:
            continue

        # ---------------------------------------------
        # Tamaño típico de los campos
        # ---------------------------------------------

        if not (
            12
            <= rectangulo.height
            <= 35
        ):
            continue

        # ---------------------------------------------
        # Evitar dibujos demasiado pequeños
        # ---------------------------------------------

        if rectangulo.width < 70:
            continue

        # ---------------------------------------------
        # Evitar elementos demasiado anchos
        # ---------------------------------------------

        if rectangulo.width > (
            pagina.rect.width * 0.85
        ):
            continue

        # ---------------------------------------------
        # Debe existir borde
        # ---------------------------------------------

        if dibujo.get("color") is None:
            continue

        candidatos.append(
            rectangulo
        )

    candidatos = eliminar_duplicados(
        candidatos
    )

    filas = agrupar_por_filas(
        candidatos
    )

    # =====================================================
    # ESTRUCTURA ESPERADA
    #
    # fila 1 → Fecha | Documento
    # fila 2 → Nombre
    # fila 3 → Colegio
    # fila 4 → Evaluación | Grupo | Grado
    # fila 5 → Sesión | contador | Ciudad
    # =====================================================

    estructura_esperada = [
        2,
        1,
        1,
        3,
        3,
    ]

    filas_validas = None

    for inicio in range(
        len(filas) - 4
    ):

        grupo = filas[
            inicio:
            inicio + 5
        ]

        cantidades = [
            len(fila)
            for fila in grupo
        ]

        if (
            cantidades
            == estructura_esperada
        ):

            filas_validas = grupo
            break

    if filas_validas is None:

        raise ValueError(
            "No se pudo detectar automáticamente "
            "la estructura del encabezado VisionU."
        )

    fila_1 = filas_validas[0]
    fila_2 = filas_validas[1]
    fila_3 = filas_validas[2]
    fila_4 = filas_validas[3]
    fila_5 = filas_validas[4]

    return {

        # Fecha | Documento

        "fecha":
            fila_1[0],

        "documento":
            fila_1[1],

        # Nombre

        "nombre":
            fila_2[0],

        # Colegio

        "colegio":
            fila_3[0],

        # Evaluación | Grupo | Grado

        "evaluacion":
            fila_4[0],

        "grupo":
            fila_4[1],

        "grado":
            fila_4[2],

        # Sesión | contador | Ciudad

        "sesion":
            fila_5[0],

        "contador":
            fila_5[1],

        "ciudad":
            fila_5[2],
    }


# =========================================================
# CALCULAR TAMAÑO DE FUENTE
# =========================================================

def calcular_tamano_fuente(
    texto,
    ancho_disponible,
):

    tamano = TAMANO_MAXIMO

    while tamano >= TAMANO_MINIMO:

        ancho_texto = (
            pymupdf.get_text_length(
                texto,
                fontname=FUENTE,
                fontsize=tamano,
            )
        )

        if (
            ancho_texto
            <= ancho_disponible
        ):

            return tamano

        tamano -= 0.2

    return TAMANO_MINIMO


# =========================================================
# ESCRIBIR UN CAMPO
# =========================================================

def escribir_campo(
    pagina,
    rectangulo,
    texto,
    offset_mm,
):

    if texto is None:
        return

    texto = str(
        texto
    ).strip()

    if texto == "":
        return

    # Posición horizontal
    x = (
        rectangulo.x0
        + mm_a_pt(
            offset_mm
        )
    )

    margen_derecho = (
        mm_a_pt(1.2)
    )

    ancho_disponible = (
        rectangulo.x1
        - margen_derecho
        - x
    )

    if ancho_disponible <= 0:
        return

    tamano_fuente = (
        calcular_tamano_fuente(
            texto,
            ancho_disponible,
        )
    )

    # Posición vertical
    y = (
        rectangulo.y0
        + rectangulo.height
        * 0.70
    )

    pagina.insert_text(
        (
            x,
            y,
        ),
        texto,
        fontname=FUENTE,
        fontsize=tamano_fuente,
        color=(0, 0, 0),
    )


# =========================================================
# ESCRIBIR CONTADOR CENTRADO
# =========================================================

def escribir_contador(
    pagina,
    rectangulo,
    texto,
):

    tamano = TAMANO_MAXIMO

    ancho_texto = (
        pymupdf.get_text_length(
            texto,
            fontname=FUENTE,
            fontsize=tamano,
        )
    )

    x = (
        rectangulo.x0
        +
        (
            rectangulo.width
            - ancho_texto
        ) / 2
    )

    y = (
        rectangulo.y0
        + rectangulo.height
        * 0.70
    )

    pagina.insert_text(
        (
            x,
            y,
        ),
        texto,
        fontname=FUENTE,
        fontsize=tamano,
        color=(0, 0, 0),
    )


# =========================================================
# LLENAR ENCABEZADO
# =========================================================

def llenar_encabezado(
    pagina,
    estudiante,
    lote,
    numero_estudiante,
    total_estudiantes,
):

    campos = (
        detectar_campos_encabezado(
            pagina
        )
    )

    datos = {

        "fecha":
            lote.fecha,

        "documento":
            estudiante.documento,

        "nombre":
            estudiante.nombre,

        "colegio":
            estudiante.colegio,

        "evaluacion":
            lote.prueba,

        "grupo":
            estudiante.grupo,

        "grado":
            estudiante.grado,

        "sesion":
            lote.sesion,

        "ciudad":
            estudiante.ciudad,
    }

    for (
        nombre_campo,
        texto,
    ) in datos.items():

        escribir_campo(
            pagina,
            campos[
                nombre_campo
            ],
            texto,
            OFFSET_CAMPOS_MM[
                nombre_campo
            ],
        )

    contador = (
        f"{numero_estudiante} "
        f"de {total_estudiantes}"
    )

    escribir_contador(
        pagina,
        campos["contador"],
        contador,
    )


# =========================================================
# GENERAR PREMARCADO COMPLETO
# =========================================================

def generar_premark(
    ruta_plantilla,
    lote,
    ruta_salida,
    progreso_callback=None,
):

    # =====================================================
    # VALIDACIONES
    # =====================================================

    if not lote.estudiantes:

        raise ValueError(
            "El lote no contiene estudiantes."
        )

    # =====================================================
    # ABRIR PLANTILLA
    # =====================================================

    plantilla = pymupdf.open(
        ruta_plantilla
    )

    if len(plantilla) == 0:

        plantilla.close()

        raise ValueError(
            "La plantilla PDF está vacía."
        )

    # =====================================================
    # CREAR DOCUMENTO FINAL
    # =====================================================

    documento_final = (
        pymupdf.open()
    )

    total_estudiantes = len(
        lote.estudiantes
    )

    try:

        # =================================================
        # UNA PÁGINA POR ESTUDIANTE
        # =================================================

        for (
            indice,
            estudiante,
        ) in enumerate(
            lote.estudiantes,
            start=1,
        ):

            print()

            print(
                f"Generando {indice} "
                f"de {total_estudiantes}: "
                f"{estudiante.nombre}"
            )

            # =============================================
            # COPIAR PLANTILLA
            # =============================================

            documento_final.insert_pdf(
                plantilla,
                from_page=0,
                to_page=0,
            )

            pagina = (
                documento_final[-1]
            )

            # =============================================
            # ENCABEZADO
            # =============================================

            llenar_encabezado(
                pagina,
                estudiante,
                lote,
                indice,
                total_estudiantes,
            )

            # =============================================
            # QR
            # =============================================

            insertar_qr(
                pagina,
                estudiante,
                lote,
                indice,
                total_estudiantes,
            )

            # =============================================
            # GUÍAS OMR
            # =============================================

            informacion = (
                aplicar_guias(
                    pagina
                )
            )

            # =============================================
            # MOSTRAR ESTRUCTURA SOLO UNA VEZ
            # =============================================

            if indice == 1:

                print()

                print(
                    "Estructura detectada:"
                )

                print(
                    "Preguntas:",
                    informacion[
                        "preguntas"
                    ],
                )

                print(
                    "Bloques:",
                    informacion[
                        "marcos"
                    ],
                )

                print(
                    "Opciones:",
                    informacion[
                        "opciones"
                    ],
                )

                print()

            # =============================================
            # REPORTAR PROGRESO
            # =============================================

            if (
                progreso_callback
                is not None
            ):

                progreso_callback(
                    indice,
                    total_estudiantes,
                )

        # =================================================
        # GUARDAR PDF
        # =================================================

        documento_final.save(
            ruta_salida
        )

        print()

        print(
            "======================================"
        )

        print(
            "PDF generado correctamente"
        )

        print(
            "Estudiantes:",
            total_estudiantes,
        )

        print(
            "Salida:",
            ruta_salida,
        )

        print(
            "======================================"
        )

    finally:

        # =================================================
        # CERRAR DOCUMENTOS SIEMPRE
        # =================================================

        documento_final.close()

        plantilla.close()