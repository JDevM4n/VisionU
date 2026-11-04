const API_URL =
  "http://127.0.0.1:8000";


// =========================================================
// HEALTH
// =========================================================

export async function verificarBackend() {

  const respuesta =
    await fetch(
      `${API_URL}/health`
    );


  if (!respuesta.ok) {

    throw new Error(
      "Backend no disponible."
    );

  }


  return respuesta.json();
}


// =========================================================
// ANALIZAR EXCEL
// =========================================================

export async function analizarExcel({
  excel,
  hoja,
}) {

  const datos =
    new FormData();


  datos.append(
    "excel",
    excel
  );


  datos.append(
    "hoja",
    hoja
  );


  let respuesta;


  try {

    respuesta =
      await fetch(

        `${API_URL}/excel/preview`,

        {
          method: "POST",
          body: datos,
        }

      );


  } catch {

    throw new Error(
      "No se pudo conectar "
      + "con VisionU."
    );

  }


  if (!respuesta.ok) {

    const error =
      await respuesta.json();


    throw new Error(

      error.detail
      ||
      "No se pudo analizar el Excel."

    );

  }


  return respuesta.json();
}


// =========================================================
// INICIAR GENERACIÓN
// =========================================================

export async function iniciarPremarcado({

  plantilla,
  excel,
  fecha,
  evaluacion,
  grado,
  jornada,
  sesion,
  hoja,

}) {

  const datos =
    new FormData();


  datos.append(
    "plantilla",
    plantilla
  );


  datos.append(
    "excel",
    excel
  );


  datos.append(
    "fecha",
    fecha
  );


  datos.append(
    "evaluacion",
    evaluacion
  );


  datos.append(
    "grado",
    grado
  );


  datos.append(
    "jornada",
    jornada
  );


  datos.append(
    "sesion",
    sesion
  );


  datos.append(
    "hoja",
    hoja
  );


  const respuesta =
    await fetch(

      `${API_URL}/premarcado/iniciar`,

      {

        method: "POST",

        body: datos,

      }

    );


  if (!respuesta.ok) {

    const error =
      await respuesta.json();


    throw new Error(

      error.detail
      ||
      "No fue posible iniciar "
      + "el premarcado."

    );

  }


  return respuesta.json();
}


// =========================================================
// CONSULTAR PROGRESO
// =========================================================

export async function obtenerEstadoPremarcado(
  jobId
) {

  const respuesta =
    await fetch(

      `${API_URL}/premarcado/estado/${jobId}`

    );


  if (!respuesta.ok) {

    const error =
      await respuesta.json();


    throw new Error(

      error.detail
      ||
      "No fue posible consultar "
      + "el progreso."

    );

  }


  return respuesta.json();
}


// =========================================================
// DESCARGAR PDF
// =========================================================

export async function descargarPremarcado(
  jobId
) {

  const respuesta =
    await fetch(

      `${API_URL}/premarcado/descargar/${jobId}`

    );


  if (!respuesta.ok) {

    const error =
      await respuesta.json();


    throw new Error(

      error.detail
      ||
      "No fue posible descargar "
      + "el PDF."

    );

  }


  return respuesta.blob();
}