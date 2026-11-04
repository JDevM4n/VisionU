import io
import qrcode


def construir_contenido_qr(
    estudiante,
    lote,
    numero_estudiante,
    total_estudiantes
):

    contador = (
        f"{numero_estudiante} de {total_estudiantes}"
    )

    contenido = ",".join([
        str(lote.fecha).strip(),
        str(estudiante.documento).strip(),
        str(estudiante.nombre).strip(),
        str(estudiante.colegio).strip(),
        str(lote.prueba).strip(),
        str(estudiante.grado).strip(),
        str(estudiante.grupo).strip(),
        str(lote.jornada).strip(),
        contador,
        str(estudiante.ciudad).strip()
    ])

    return contenido


def generar_qr_bytes(
    estudiante,
    lote,
    numero_estudiante,
    total_estudiantes
):

    contenido = construir_contenido_qr(
        estudiante,
        lote,
        numero_estudiante,
        total_estudiantes
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2
    )

    qr.add_data(
        contenido
    )

    qr.make(
        fit=True
    )

    imagen = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()

    imagen.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue(), contenido