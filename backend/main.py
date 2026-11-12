import os
import shutil
import threading
import time
import uuid

from datetime import datetime
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.responses import (
    FileResponse,
)


from domain.Lote import Lote

from infrastructure.excel_reader import (
    agregar_estudiantes,
)

from services.premark_service import (
    generar_premark,
)


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="VisionU API",
    version="2.0.0",
)


# =========================================================
# CORS
# =========================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://127.0.0.1:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CARPETAS
# =========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)


TEMP_DIR = (
    BASE_DIR
    / "storage"
    / "temp"
)


TEMP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# TRABAJOS DE GENERACIÓN
# =========================================================

trabajos = {}

trabajos_lock = (
    threading.Lock()
)


# =========================================================
# ACTUALIZAR ESTADO DE UN TRABAJO
# =========================================================

def actualizar_trabajo(
    job_id,
    **datos,
):

    with trabajos_lock:

        if job_id not in trabajos:
            return

        trabajos[job_id].update(
            datos
        )


# =========================================================
# GUARDAR ARCHIVO
# =========================================================

async def guardar_upload(
    archivo,
    ruta,
):

    contenido = (
        await archivo.read()
    )

    with open(
        ruta,
        "wb",
    ) as destino:

        destino.write(
            contenido
        )


# =========================================================
# HEALTH
# =========================================================

@app.get("/")
def inicio():

    return {

        "nombre":
            "VisionU API",

        "estado":
            "online",

        "version":
            "2.0.0",

    }


@app.get("/health")
def health():

    return {

        "status": "ok"

    }


# =========================================================
# PREVIEW DEL EXCEL
# =========================================================

@app.post(
    "/excel/preview"
)

@app.post("/excel/preview")
async def preview_excel(
    excel: UploadFile = File(...),
    hoja: str = Form(...),
    grado: str = Form(...),
):

    identificador = (
        str(uuid.uuid4())
    )


    carpeta = (
        TEMP_DIR
        / identificador
    )


    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )


    extension = (

        Path(
            excel.filename
        )
        .suffix
        .lower()

    )


    if extension not in [
        ".xlsx",
        ".xlsm",
    ]:

        shutil.rmtree(
            carpeta,
            ignore_errors=True,
        )

        raise HTTPException(

            status_code=400,

            detail=(
                "El archivo debe ser "
                "Excel (.xlsx o .xlsm)."
            ),

        )


    ruta_excel = (

        carpeta
        / f"estudiantes{extension}"

    )


    try:

        await guardar_upload(
            excel,
            ruta_excel,
        )


        estudiantes = agregar_estudiantes(
            str(ruta_excel),
            hoja,
            grado,
        )


        # IMPORTANTE:
        # enviamos TODOS.
        # React se encarga de paginar de 10.

        preview = []


        for estudiante in estudiantes:

            preview.append({

                "documento":
                    estudiante.documento,

                "nombre":
                    estudiante.nombre,

                "colegio":
                    estudiante.colegio,

                "grupo":
                    estudiante.grupo,

                "grado":
                    estudiante.grado,

                "ciudad":
                    estudiante.ciudad,

            })


        return {

            "cantidad":
                len(estudiantes),

            "estudiantes":
                preview,

        }


    except Exception as error:

        raise HTTPException(

            status_code=400,

            detail=str(error),

        )


    finally:

        shutil.rmtree(
            carpeta,
            ignore_errors=True,
        )


# =========================================================
# PROCESAR PREMARCADO EN SEGUNDO HILO
# =========================================================

def procesar_premark(

    job_id,

    ruta_plantilla,

    ruta_excel,

    ruta_salida,

    fecha,

    evaluacion,

    grado,

    jornada,

    sesion,

    hoja,

):

    tiempo_inicio = (
        time.time()
    )


    try:

        # =================================================
        # LEER ESTUDIANTES
        # =================================================

        actualizar_trabajo(

            job_id,

            estado="procesando",

            mensaje=(
                "Leyendo listado "
                "de estudiantes..."
            ),

        )


        estudiantes = (
            agregar_estudiantes(
                str(ruta_excel),
                hoja,
                grado,
            )
        )


        total = len(
            estudiantes
        )


        if total == 0:

            raise ValueError(
                "No se encontraron estudiantes."
            )


        actualizar_trabajo(

            job_id,

            total=total,

            procesados=0,

            porcentaje=0,

            eta_segundos=None,

            mensaje=(
                "Preparando generación..."
            ),

        )


        # =================================================
        # FECHA
        # =================================================

        fecha_objeto = (
            datetime.strptime(
                fecha,
                "%Y-%m-%d",
            )
        )


        fecha_visionu = (
            fecha_objeto.strftime(
                "%d/%m/%Y"
            )
        )


        # =================================================
        # LOTE
        # =================================================

        lote = Lote(

            fecha_visionu,

            evaluacion,

            grado,

            jornada,

            sesion,

            estudiantes,

        )


        # =================================================
        # CALLBACK DE PROGRESO
        # =================================================

        def progreso_callback(
            procesados,
            total_estudiantes,
        ):

            ahora = (
                time.time()
            )


            transcurrido = (
                ahora
                - tiempo_inicio
            )


            if procesados > 0:

                promedio = (

                    transcurrido
                    / procesados

                )

                faltantes = (

                    total_estudiantes
                    - procesados

                )

                eta = (

                    promedio
                    * faltantes

                )

            else:

                eta = None


            # Dejamos 5 % para guardar
            # y finalizar el PDF.

            porcentaje = int(

                (
                    procesados
                    / total_estudiantes
                )
                * 95

            )


            actualizar_trabajo(

                job_id,

                estado="procesando",

                procesados=procesados,

                total=total_estudiantes,

                porcentaje=porcentaje,

                tiempo_transcurrido=(
                    int(transcurrido)
                ),

                eta_segundos=(
                    int(eta)
                    if eta is not None
                    else None
                ),

                mensaje=(

                    f"Procesando estudiante "
                    f"{procesados} "
                    f"de {total_estudiantes}"

                ),

            )


        # =================================================
        # GENERAR
        # =================================================

        generar_premark(

            str(ruta_plantilla),

            lote,

            str(ruta_salida),

            progreso_callback=
                progreso_callback,

        )


        # =================================================
        # COMPLETADO
        # =================================================

        tiempo_total = int(

            time.time()
            - tiempo_inicio

        )


        actualizar_trabajo(

            job_id,

            estado="completado",

            procesados=total,

            total=total,

            porcentaje=100,

            tiempo_transcurrido=
                tiempo_total,

            eta_segundos=0,

            mensaje=(
                "Premarcado generado "
                "correctamente."
            ),

            ruta_salida=
                str(ruta_salida),

        )


    except Exception as error:

        print(
            "ERROR GENERACIÓN:",
            error,
        )


        actualizar_trabajo(

            job_id,

            estado="error",

            mensaje=str(error),

            error=str(error),

        )


# =========================================================
# INICIAR PREMARCADO
# =========================================================

@app.post(
    "/premarcado/iniciar"
)
async def iniciar_premark(

    plantilla: UploadFile = File(...),

    excel: UploadFile = File(...),

    fecha: str = Form(...),

    evaluacion: str = Form(...),

    grado: str = Form(...),

    jornada: str = Form(...),

    sesion: str = Form(...),

    hoja: str = Form(...),

):

    # =====================================================
    # VALIDACIONES
    # =====================================================

    extension_pdf = (

        Path(
            plantilla.filename
        )
        .suffix
        .lower()

    )


    if extension_pdf != ".pdf":

        raise HTTPException(

            status_code=400,

            detail=(
                "La plantilla debe ser PDF."
            ),

        )


    extension_excel = (

        Path(
            excel.filename
        )
        .suffix
        .lower()

    )


    if extension_excel not in [

        ".xlsx",
        ".xlsm",

    ]:

        raise HTTPException(

            status_code=400,

            detail=(
                "El listado debe ser Excel."
            ),

        )


    # =====================================================
    # JOB
    # =====================================================

    job_id = (
        str(uuid.uuid4())
    )


    carpeta = (
        TEMP_DIR
        / job_id
    )


    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )


    ruta_plantilla = (

        carpeta
        / "plantilla.pdf"

    )


    ruta_excel = (

        carpeta
        / (
            "estudiantes"
            + extension_excel
        )

    )


    ruta_salida = (

        carpeta
        / "Premarcado_VisionU.pdf"

    )


    # =====================================================
    # GUARDAR ARCHIVOS
    # =====================================================

    await guardar_upload(
        plantilla,
        ruta_plantilla,
    )


    await guardar_upload(
        excel,
        ruta_excel,
    )


    # =====================================================
    # CREAR ESTADO
    # =====================================================

    with trabajos_lock:

        trabajos[job_id] = {

            "job_id":
                job_id,

            "estado":
                "preparando",

            "procesados":
                0,

            "total":
                0,

            "porcentaje":
                0,

            "tiempo_transcurrido":
                0,

            "eta_segundos":
                None,

            "mensaje":
                "Preparando generación...",

            "ruta_salida":
                None,

            "error":
                None,

        }


    # =====================================================
    # HILO DE GENERACIÓN
    # =====================================================

    hilo = threading.Thread(

        target=
            procesar_premark,

        args=(

            job_id,

            ruta_plantilla,

            ruta_excel,

            ruta_salida,

            fecha,

            evaluacion,

            grado,

            jornada,

            sesion,

            hoja,

        ),

        daemon=True,

    )


    hilo.start()


    # =====================================================
    # RESPUESTA INMEDIATA
    # =====================================================

    return {

        "job_id":
            job_id

    }


# =========================================================
# CONSULTAR ESTADO
# =========================================================

@app.get(
    "/premarcado/estado/{job_id}"
)
def estado_premark(
    job_id: str,
):

    with trabajos_lock:

        trabajo = (
            trabajos.get(
                job_id
            )
        )


        if trabajo is None:

            raise HTTPException(

                status_code=404,

                detail=(
                    "Trabajo no encontrado."
                ),

            )


        # Copia para no devolver
        # referencia mutable.

        return dict(
            trabajo
        )


# =========================================================
# DESCARGAR RESULTADO
# =========================================================

@app.get(
    "/premarcado/descargar/{job_id}"
)
def descargar_premark(
    job_id: str,
):

    with trabajos_lock:

        trabajo = (
            trabajos.get(
                job_id
            )
        )


    if trabajo is None:

        raise HTTPException(

            status_code=404,

            detail=(
                "Trabajo no encontrado."
            ),

        )


    if (
        trabajo["estado"]
        != "completado"
    ):

        raise HTTPException(

            status_code=400,

            detail=(
                "El premarcado todavía "
                "no está listo."
            ),

        )


    ruta = Path(
        trabajo["ruta_salida"]
    )


    if not ruta.exists():

        raise HTTPException(

            status_code=404,

            detail=(
                "El PDF generado "
                "no fue encontrado."
            ),

        )


    return FileResponse(

        path=str(ruta),

        media_type=(
            "application/pdf"
        ),

        filename=(
            "Premarcado_VisionU.pdf"
        ),

    )