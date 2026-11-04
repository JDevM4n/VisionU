import pymupdf
from collections import Counter


# =========================================================
# CONFIGURACIÓN DE GUÍAS
# =========================================================

ANCHO_SUPERIOR_MM = 2.8
ALTO_SUPERIOR_MM = 2.8

ANCHO_LATERAL_MM = 3.5
ALTO_LATERAL_MM = 3.5


# Distancia entre el marco real y los cuadros negros
ESPACIO_SUPERIOR_MM = 0.8
ESPACIO_INFERIOR_MM = 0.8
ESPACIO_IZQUIERDO_MM = 0.8
ESPACIO_DERECHO_MM = 0.8


# Margen mínimo respecto al borde físico de la página
MARGEN_BORDE_PAGINA_MM = 1.0


# =========================================================
# CONVERSIONES
# =========================================================

def mm_a_pt(mm):
    return mm * 72 / 25.4


# =========================================================
# AGRUPAR COORDENADAS CERCANAS
# =========================================================

def agrupar_valores(valores, tolerancia):

    grupos = []

    for valor in sorted(valores):

        if not grupos:
            grupos.append([valor])
            continue

        promedio = sum(grupos[-1]) / len(grupos[-1])

        if abs(valor - promedio) <= tolerancia:
            grupos[-1].append(valor)

        else:
            grupos.append([valor])

    centros = []

    for grupo in grupos:
        centros.append(
            sum(grupo) / len(grupo)
        )

    return centros


# =========================================================
# DETECTAR BURBUJAS
# =========================================================

def detectar_burbujas(pagina):

    candidatos = []

    for dibujo in pagina.get_drawings():

        rectangulo = dibujo["rect"]

        relleno = dibujo.get("fill")

        if relleno is None:
            continue

        # Interior aproximadamente blanco
        if not all(
            componente >= 0.95
            for componente in relleno
        ):
            continue

        # Tamaño probable de burbuja
        if not (
            6 <= rectangulo.width <= 24
            and
            6 <= rectangulo.height <= 24
        ):
            continue

        # Debe ser prácticamente circular
        if abs(
            rectangulo.width
            - rectangulo.height
        ) > 0.8:
            continue

        cantidad_curvas = sum(
            1
            for elemento in dibujo["items"]
            if elemento[0] == "c"
        )

        if cantidad_curvas < 4:
            continue

        candidatos.append(dibujo)

    if not candidatos:
        raise ValueError(
            "No se encontraron burbujas en el PDF"
        )

    # =====================================================
    # TAMAÑO DE BURBUJA MÁS COMÚN
    # =====================================================

    tamaños = Counter(
        round(
            dibujo["rect"].width * 2
        ) / 2
        for dibujo in candidatos
    )

    cantidad_mayor = max(
        tamaños.values()
    )

    tamaños_mas_comunes = [
        tamaño
        for tamaño, cantidad in tamaños.items()
        if cantidad == cantidad_mayor
    ]

    diametro_referencia = max(
        tamaños_mas_comunes
    )

    # =====================================================
    # FILTRADO FINAL
    # =====================================================

    burbujas = []

    for dibujo in candidatos:

        rectangulo = dibujo["rect"]

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

    return burbujas, diametro_referencia


# =========================================================
# DETECTAR MARCOS DE PREGUNTAS
# =========================================================

def detectar_marcos(
    pagina,
    burbujas,
    diametro
):

    ancho_pagina = pagina.rect.width
    alto_pagina = pagina.rect.height

    candidatos = []

    for dibujo in pagina.get_drawings():

        rectangulo = dibujo["rect"]

        # El marco no debe tener relleno
        if dibujo.get("fill") is not None:
            continue

        # Debe tener borde
        if dibujo.get("color") is None:
            continue

        # Mucho más grande que una burbuja
        if rectangulo.width < diametro * 2.5:
            continue

        if rectangulo.height < diametro * 3:
            continue

        # Evitar detectar la página completa
        if rectangulo.width > ancho_pagina * 0.90:
            continue

        if rectangulo.height > alto_pagina * 0.90:
            continue

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

        if len(burbujas_dentro) < 4:
            continue

        candidatos.append({
            "rect": rectangulo,
            "burbujas": burbujas_dentro
        })

    if not candidatos:
        raise ValueError(
            "No se encontraron los marcos de preguntas"
        )

    candidatos.sort(
        key=lambda elemento:
        elemento["rect"].x0
    )

    # =====================================================
    # ELIMINAR DUPLICADOS
    # =====================================================

    marcos = []

    for candidato in candidatos:

        rectangulo = candidato["rect"]

        duplicado = False

        for marco in marcos:

            anterior = marco["rect"]

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

        burbujas = marco["burbujas"]

        columnas = agrupar_valores(
            [
                burbuja["x"]
                for burbuja in burbujas
            ],
            tolerancia
        )

        filas = agrupar_valores(
            [
                burbuja["y"]
                for burbuja in burbujas
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
# OBTENER FILAS GLOBALES
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
            for burbuja in burbujas
        ],
        tolerancia
    )


# =========================================================
# POSICIÓN ANTES DEL MARCO
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

    if espacio_disponible < tamaño_marca:

        raise ValueError(
            "No hay espacio suficiente "
            "antes del marco."
        )

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
# POSICIÓN DESPUÉS DEL MARCO
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

    if espacio_disponible < tamaño_marca:

        raise ValueError(
            "No hay espacio suficiente "
            "después del marco."
        )

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
# DIBUJAR CUADRO NEGRO
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
    # ARRIBA Y ABAJO DE CADA BLOQUE
    # =====================================================

    for marco in marcos:

        rectangulo = marco["rect"]
        columnas = marco["columnas"]

        y_superior = posicion_antes_marco(
            rectangulo.y0,
            alto_superior,
            espacio_superior,
            margen_pagina
        )

        y_inferior = posicion_despues_marco(
            rectangulo.y1,
            alto_superior,
            espacio_inferior,
            pagina.rect.height
            - margen_pagina
        )

        for centro_x in columnas:

            x = (
                centro_x
                - ancho_superior / 2
            )

            # Arriba
            dibujar_marca(
                pagina,
                x,
                y_superior,
                ANCHO_SUPERIOR_MM,
                ALTO_SUPERIOR_MM
            )

            # Abajo
            dibujar_marca(
                pagina,
                x,
                y_inferior,
                ANCHO_SUPERIOR_MM,
                ALTO_SUPERIOR_MM
            )

    # =====================================================
    # MARCOS EXTERNOS
    # =====================================================

    primer_marco = min(
        marcos,
        key=lambda marco:
        marco["rect"].x0
    )

    ultimo_marco = max(
        marcos,
        key=lambda marco:
        marco["rect"].x1
    )

    # =====================================================
    # IZQUIERDA
    # =====================================================

    x_izquierda = posicion_antes_marco(
        primer_marco["rect"].x0,
        ancho_lateral,
        espacio_izquierdo,
        margen_pagina
    )

    # =====================================================
    # DERECHA
    # =====================================================

    x_derecha = posicion_despues_marco(
        ultimo_marco["rect"].x1,
        ancho_lateral,
        espacio_derecho,
        pagina.rect.width
        - margen_pagina
    )

    filas = obtener_filas_globales(
        burbujas,
        diametro
    )

    # =====================================================
    # LATERALES
    # =====================================================

    for centro_y in filas:

        y = (
            centro_y
            - alto_lateral / 2
        )

        dibujar_marca(
            pagina,
            x_izquierda,
            y,
            ANCHO_LATERAL_MM,
            ALTO_LATERAL_MM
        )

        dibujar_marca(
            pagina,
            x_derecha,
            y,
            ANCHO_LATERAL_MM,
            ALTO_LATERAL_MM
        )


# =========================================================
# FUNCIÓN PÚBLICA
# =========================================================

def aplicar_guias(pagina):

    """
    Recibe una página de PyMuPDF y agrega
    automáticamente todas las guías OMR.
    """

    # 1. Burbujas
    burbujas, diametro = detectar_burbujas(
        pagina
    )

    # 2. Marcos
    marcos_detectados = detectar_marcos(
        pagina,
        burbujas,
        diametro
    )

    # 3. Estructura
    marcos = analizar_marcos(
        marcos_detectados,
        diametro
    )

    # 4. Guías
    dibujar_marcas(
        pagina,
        marcos,
        burbujas,
        diametro
    )

    # Información útil para consola
    preguntas = sum(
        len(marco["filas"])
        for marco in marcos
    )

    return {
        "burbujas": len(burbujas),
        "marcos": len(marcos),
        "preguntas": preguntas,
        "opciones": [
            len(marco["columnas"])
            for marco in marcos
        ]
    }