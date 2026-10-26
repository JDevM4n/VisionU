import pymupdf

from collections import Counter


# =========================================================
# CONFIGURACIÓN
# =========================================================

RUTA_ENTRADA = (
    "D:\\Trabajo\\VisionU\\AppVisionU\\inputs\\Hoja1_9.pdf"
)

RUTA_SALIDA = (
    "D:\\Trabajo\\VisionU\\AppVisionU\\outputs\\Hoja1_9_premark.pdf"
)


# =========================================================
# TAMAÑO DE LAS MARCAS NEGRAS
# =========================================================

# Cuadros superiores e inferiores
ANCHO_SUPERIOR_MM = 2.8
ALTO_SUPERIOR_MM = 2.8


# Cuadros laterales
ANCHO_LATERAL_MM = 3.5
ALTO_LATERAL_MM = 3.5


# =========================================================
# ESPACIO ENTRE MARCO Y CUADRO NEGRO
# =========================================================

# Estos son los valores que normalmente modificarías.

# Distancia desde el borde superior del cuadro
ESPACIO_SUPERIOR_MM = 0.8

# Distancia desde el borde inferior del cuadro
ESPACIO_INFERIOR_MM = 0.8

# Distancia desde el borde izquierdo del cuadro
ESPACIO_IZQUIERDO_MM = 0.8

# Distancia desde el borde derecho del cuadro
ESPACIO_DERECHO_MM = 0.8


# =========================================================
# SEGURIDAD DE PÁGINA
# =========================================================

# Nunca permite que una marca quede completamente
# pegada al borde físico del PDF.

MARGEN_BORDE_PAGINA_MM = 1.0


# =========================================================
# CONVERSIONES
# =========================================================

def mm_a_pt(mm):

    return mm * 72 / 25.4


# =========================================================
# AGRUPAR COORDENADAS CERCANAS
# =========================================================

def agrupar_valores(
    valores,
    tolerancia
):

    grupos = []


    for valor in sorted(valores):


        if not grupos:

            grupos.append(
                [valor]
            )

            continue


        promedio = (
            sum(grupos[-1])
            / len(grupos[-1])
        )


        if abs(
            valor - promedio
        ) <= tolerancia:

            grupos[-1].append(
                valor
            )


        else:

            grupos.append(
                [valor]
            )


    centros = []


    for grupo in grupos:

        centros.append(

            sum(grupo)
            / len(grupo)

        )


    return centros


# =========================================================
# DETECTAR BURBUJAS DE RESPUESTA
# =========================================================

def detectar_burbujas(
    pagina
):

    candidatos = []


    # =====================================================
    # BUSCAR FIGURAS CIRCULARES
    # =====================================================

    for dibujo in pagina.get_drawings():

        rectangulo = dibujo["rect"]

        relleno = dibujo.get(
            "fill"
        )


        # Debe tener relleno
        if relleno is None:
            continue


        # Las burbujas tienen interior blanco.
        if not all(

            componente >= 0.95

            for componente
            in relleno

        ):

            continue


        # Tamaño razonable de una burbuja.
        if not (

            6 <= rectangulo.width <= 24

            and

            6 <= rectangulo.height <= 24

        ):

            continue


        # Debe ser aproximadamente circular.
        if abs(

            rectangulo.width
            - rectangulo.height

        ) > 0.8:

            continue


        # Los círculos vectoriales utilizan
        # curvas Bézier.
        cantidad_curvas = sum(

            1

            for elemento
            in dibujo["items"]

            if elemento[0] == "c"

        )


        if cantidad_curvas < 4:
            continue


        candidatos.append(
            dibujo
        )


    if not candidatos:

        raise ValueError(
            "No se encontraron burbujas en el PDF"
        )


    # =====================================================
    # ENCONTRAR EL TAMAÑO MÁS COMÚN DE BURBUJA
    # =====================================================

    tamaños = Counter(

        round(
            dibujo["rect"].width * 2
        ) / 2

        for dibujo
        in candidatos

    )


    cantidad_mayor = max(
        tamaños.values()
    )


    tamaños_mas_comunes = [

        tamaño

        for tamaño, cantidad
        in tamaños.items()

        if cantidad == cantidad_mayor

    ]


    # Si hay empate escogemos el círculo exterior,
    # que normalmente es el más grande.

    diametro_referencia = max(
        tamaños_mas_comunes
    )


    # =====================================================
    # FILTRAR BURBUJAS REALES
    # =====================================================

    burbujas = []


    for dibujo in candidatos:

        rectangulo = dibujo[
            "rect"
        ]


        if abs(

            rectangulo.width
            - diametro_referencia

        ) > 0.4:

            continue


        centro_x = (

            rectangulo.x0
            + rectangulo.x1

        ) / 2


        centro_y = (

            rectangulo.y0
            + rectangulo.y1

        ) / 2


        burbujas.append({

            "x": centro_x,

            "y": centro_y,

            "x0": rectangulo.x0,

            "y0": rectangulo.y0,

            "x1": rectangulo.x1,

            "y1": rectangulo.y1

        })


    if len(burbujas) < 4:

        raise ValueError(
            "Se detectaron muy pocas burbujas"
        )


    return (
        burbujas,
        diametro_referencia
    )


# =========================================================
# DETECTAR MARCOS REALES DE PREGUNTAS
# =========================================================

def detectar_marcos(
    pagina,
    burbujas,
    diametro
):

    ancho_pagina = (
        pagina.rect.width
    )

    alto_pagina = (
        pagina.rect.height
    )


    candidatos = []


    for dibujo in pagina.get_drawings():

        rectangulo = dibujo[
            "rect"
        ]


        # =================================================
        # EL MARCO NO DEBE TENER RELLENO
        # =================================================

        if dibujo.get(
            "fill"
        ) is not None:

            continue


        # =================================================
        # DEBE TENER BORDE
        # =================================================

        if dibujo.get(
            "color"
        ) is None:

            continue


        # =================================================
        # DEBE SER MÁS GRANDE QUE UNA BURBUJA
        # =================================================

        if rectangulo.width < (
            diametro * 2.5
        ):

            continue


        if rectangulo.height < (
            diametro * 3
        ):

            continue


        # =================================================
        # EVITAR DETECTAR TODA LA PÁGINA
        # =================================================

        if rectangulo.width > (
            ancho_pagina * 0.90
        ):

            continue


        if rectangulo.height > (
            alto_pagina * 0.90
        ):

            continue


        # =================================================
        # VER CUÁNTAS BURBUJAS ESTÁN DENTRO
        # =================================================

        burbujas_dentro = []


        for burbuja in burbujas:


            if (

                rectangulo.x0 - 1
                <= burbuja["x"]
                <= rectangulo.x1 + 1

                and

                rectangulo.y0 - 1
                <= burbuja["y"]
                <= rectangulo.y1 + 1

            ):

                burbujas_dentro.append(
                    burbuja
                )


        # Si no contiene suficientes burbujas,
        # no es un bloque de preguntas.

        if len(
            burbujas_dentro
        ) < 4:

            continue


        candidatos.append({

            "rect": rectangulo,

            "burbujas": burbujas_dentro

        })


    if not candidatos:

        raise ValueError(
            "No se encontraron los marcos de preguntas"
        )


    # =====================================================
    # ORDENAR DE IZQUIERDA A DERECHA
    # =====================================================

    candidatos.sort(

        key=lambda elemento:
        elemento["rect"].x0

    )


    # =====================================================
    # ELIMINAR MARCOS DUPLICADOS
    # =====================================================

    marcos = []


    for candidato in candidatos:

        rectangulo = candidato[
            "rect"
        ]


        duplicado = False


        for marco in marcos:

            anterior = marco[
                "rect"
            ]


            diferencia = max(

                abs(
                    rectangulo.x0
                    - anterior.x0
                ),

                abs(
                    rectangulo.y0
                    - anterior.y0
                ),

                abs(
                    rectangulo.x1
                    - anterior.x1
                ),

                abs(
                    rectangulo.y1
                    - anterior.y1
                )

            )


            if diferencia < 2:

                duplicado = True

                break


        if not duplicado:

            marcos.append(
                candidato
            )


    return marcos


# =========================================================
# ANALIZAR CADA MARCO
# =========================================================

def analizar_marcos(
    marcos,
    diametro
):

    tolerancia = max(

        0.8,

        diametro * 0.08

    )


    resultados = []


    for marco in marcos:


        burbujas = marco[
            "burbujas"
        ]


        # =================================================
        # COLUMNAS DE RESPUESTA
        # =================================================

        columnas = agrupar_valores(

            [

                burbuja["x"]

                for burbuja
                in burbujas

            ],

            tolerancia

        )


        # =================================================
        # FILAS DE PREGUNTAS
        # =================================================

        filas = agrupar_valores(

            [

                burbuja["y"]

                for burbuja
                in burbujas

            ],

            tolerancia

        )


        resultados.append({

            "rect": marco["rect"],

            "burbujas": burbujas,

            "columnas": columnas,

            "filas": filas

        })


    return resultados


# =========================================================
# OBTENER TODAS LAS FILAS DE LA HOJA
# =========================================================

def obtener_filas_globales(
    burbujas,
    diametro
):

    tolerancia = max(

        0.8,

        diametro * 0.08

    )


    return agrupar_valores(

        [

            burbuja["y"]

            for burbuja
            in burbujas

        ],

        tolerancia

    )


# =========================================================
# CALCULAR POSICIÓN ANTES DE UN MARCO
# =========================================================

def posicion_antes_marco(
    borde_marco,
    tamaño_marca,
    espacio_deseado,
    margen_pagina
):

    espacio_disponible = (

        borde_marco
        - margen_pagina

    )


    # La marca no cabe ni siquiera
    # sin separación.

    if espacio_disponible < tamaño_marca:

        raise ValueError(
            "No hay espacio suficiente antes del marco "
            "para colocar la marca negra."
        )


    # Si el espacio solicitado no cabe,
    # lo reducimos automáticamente.

    espacio_real = min(

        espacio_deseado,

        espacio_disponible
        - tamaño_marca

    )


    return (

        borde_marco
        - tamaño_marca
        - espacio_real

    )


# =========================================================
# CALCULAR POSICIÓN DESPUÉS DE UN MARCO
# =========================================================

def posicion_despues_marco(
    borde_marco,
    tamaño_marca,
    espacio_deseado,
    limite_pagina
):

    espacio_disponible = (

        limite_pagina
        - borde_marco

    )


    # La marca no cabe.
    if espacio_disponible < tamaño_marca:

        raise ValueError(
            "No hay espacio suficiente después del marco "
            "para colocar la marca negra."
        )


    # Reducir automáticamente el espacio
    # si el PDF tiene poco margen.

    espacio_real = min(

        espacio_deseado,

        espacio_disponible
        - tamaño_marca

    )


    return (

        borde_marco
        + espacio_real

    )


# =========================================================
# DIBUJAR MARCA NEGRA
# =========================================================

def dibujar_marca(
    pagina,
    x,
    y,
    ancho_mm,
    alto_mm
):

    ancho = mm_a_pt(
        ancho_mm
    )

    alto = mm_a_pt(
        alto_mm
    )


    rectangulo = pymupdf.Rect(

        x,
        y,

        x + ancho,
        y + alto

    )


    pagina.draw_rect(

        rectangulo,

        color=(0, 0, 0),

        fill=(0, 0, 0)

    )


# =========================================================
# DIBUJAR TODAS LAS MARCAS
# =========================================================

def dibujar_marcas(
    pagina,
    marcos,
    burbujas,
    diametro
):

    # =====================================================
    # CONVERTIR CONFIGURACIÓN A PUNTOS
    # =====================================================

    ancho_superior = mm_a_pt(
        ANCHO_SUPERIOR_MM
    )

    alto_superior = mm_a_pt(
        ALTO_SUPERIOR_MM
    )


    ancho_lateral = mm_a_pt(
        ANCHO_LATERAL_MM
    )

    alto_lateral = mm_a_pt(
        ALTO_LATERAL_MM
    )


    espacio_superior = mm_a_pt(
        ESPACIO_SUPERIOR_MM
    )

    espacio_inferior = mm_a_pt(
        ESPACIO_INFERIOR_MM
    )

    espacio_izquierdo = mm_a_pt(
        ESPACIO_IZQUIERDO_MM
    )

    espacio_derecho = mm_a_pt(
        ESPACIO_DERECHO_MM
    )


    margen_pagina = mm_a_pt(
        MARGEN_BORDE_PAGINA_MM
    )


    # =====================================================
    # SUPERIOR E INFERIOR DE CADA BLOQUE
    # =====================================================

    for marco in marcos:

        rectangulo = marco[
            "rect"
        ]

        columnas = marco[
            "columnas"
        ]


        # -------------------------------------------------
        # POSICIÓN SUPERIOR
        # -------------------------------------------------

        y_superior = posicion_antes_marco(

            rectangulo.y0,

            alto_superior,

            espacio_superior,

            margen_pagina

        )


        # -------------------------------------------------
        # POSICIÓN INFERIOR
        # -------------------------------------------------

        y_inferior = posicion_despues_marco(

            rectangulo.y1,

            alto_superior,

            espacio_inferior,

            pagina.rect.height
            - margen_pagina

        )


        # -------------------------------------------------
        # UNA MARCA POR CADA COLUMNA DE RESPUESTA
        # -------------------------------------------------

        for centro_x in columnas:


            x = (

                centro_x

                - ancho_superior / 2

            )


            # ARRIBA
            dibujar_marca(

                pagina,

                x,

                y_superior,

                ANCHO_SUPERIOR_MM,

                ALTO_SUPERIOR_MM

            )


            # ABAJO
            dibujar_marca(

                pagina,

                x,

                y_inferior,

                ANCHO_SUPERIOR_MM,

                ALTO_SUPERIOR_MM

            )


    # =====================================================
    # MARCO MÁS A LA IZQUIERDA
    # =====================================================

    primer_marco = min(

        marcos,

        key=lambda marco:
        marco["rect"].x0

    )


    # =====================================================
    # MARCO MÁS A LA DERECHA
    # =====================================================

    ultimo_marco = max(

        marcos,

        key=lambda marco:
        marco["rect"].x1

    )


    # =====================================================
    # POSICIÓN LATERAL IZQUIERDA
    # =====================================================

    x_izquierda = posicion_antes_marco(

        primer_marco["rect"].x0,

        ancho_lateral,

        espacio_izquierdo,

        margen_pagina

    )


    # =====================================================
    # POSICIÓN LATERAL DERECHA
    # =====================================================

    x_derecha = posicion_despues_marco(

        ultimo_marco["rect"].x1,

        ancho_lateral,

        espacio_derecho,

        pagina.rect.width
        - margen_pagina

    )


    # =====================================================
    # TODAS LAS FILAS DE LA HOJA
    # =====================================================

    filas = obtener_filas_globales(

        burbujas,

        diametro

    )


    # =====================================================
    # DIBUJAR LATERALES
    # =====================================================

    for centro_y in filas:


        y = (

            centro_y

            - alto_lateral / 2

        )


        # IZQUIERDA
        dibujar_marca(

            pagina,

            x_izquierda,

            y,

            ANCHO_LATERAL_MM,

            ALTO_LATERAL_MM

        )


        # DERECHA
        dibujar_marca(

            pagina,

            x_derecha,

            y,

            ANCHO_LATERAL_MM,

            ALTO_LATERAL_MM

        )


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

documento = pymupdf.open(
    RUTA_ENTRADA
)


pagina = documento[0]


# =========================================================
# 1. DETECTAR BURBUJAS
# =========================================================

burbujas, diametro = detectar_burbujas(
    pagina
)


# =========================================================
# 2. DETECTAR MARCOS
# =========================================================

marcos_detectados = detectar_marcos(

    pagina,

    burbujas,

    diametro

)


# =========================================================
# 3. ANALIZAR CADA MARCO
# =========================================================

marcos = analizar_marcos(

    marcos_detectados,

    diametro

)


# =========================================================
# INFORMACIÓN DE DEBUG
# =========================================================

print(
    "Burbujas detectadas:",
    len(burbujas)
)


print(
    "Marcos detectados:",
    len(marcos)
)


preguntas_totales = 0


for numero_marco, marco in enumerate(

    marcos,

    start=1

):


    cantidad_filas = len(
        marco["filas"]
    )


    cantidad_columnas = len(
        marco["columnas"]
    )


    preguntas_totales += (
        cantidad_filas
    )


    print(
        f"Bloque {numero_marco}:",
        f"{cantidad_filas} filas -",
        f"{cantidad_columnas} opciones"
    )


print(
    "Preguntas detectadas:",
    preguntas_totales
)


# =========================================================
# 4. DIBUJAR MARCAS
# =========================================================

dibujar_marcas(

    pagina,

    marcos,

    burbujas,

    diametro

)


# =========================================================
# 5. GUARDAR PDF
# =========================================================

documento.save(
    RUTA_SALIDA
)


documento.close()


print(
    "PDF generado correctamente"
)