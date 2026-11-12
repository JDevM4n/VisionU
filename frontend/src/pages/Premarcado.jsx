import {
  useEffect,
  useState,
} from "react";


import {
  ArrowLeft,
  FileText,
  Sparkles,
  Download,
  CheckCircle2,
} from "lucide-react";


import {
  useNavigate,
} from "react-router-dom";


import FileUpload from "../components/FileUpload";
import StudentTable from "../components/StudentTable";


import {
  analizarExcel,
  iniciarPremarcado,
  obtenerEstadoPremarcado,
  descargarPremarcado,
} from "../services/api";


function Premarcado() {

  const navigate =
    useNavigate();


  // =======================================================
  // ARCHIVOS
  // =======================================================

  const [
    plantilla,
    setPlantilla
  ] = useState(null);


  const [
    excel,
    setExcel
  ] = useState(null);


  // =======================================================
  // DATOS DEL LOTE
  // =======================================================

  const [
    evaluacion,
    setEvaluacion
  ] = useState("");


  const [
    fecha,
    setFecha
  ] = useState(
    new Date()
      .toISOString()
      .split("T")[0]
  );


  const [
    grado,
    setGrado
  ] = useState("10");


  const [
    jornada,
    setJornada
  ] = useState("Mañana");


  const [
    sesion,
    setSesion
  ] = useState("1");


  const [
    hoja,
    setHoja
  ] = useState("PU3");


  // =======================================================
  // ESTUDIANTES
  // =======================================================

  const [
    estudiantes,
    setEstudiantes
  ] = useState([]);


  const [
    cantidadEstudiantes,
    setCantidadEstudiantes
  ] = useState(0);


  const [
    cargandoEstudiantes,
    setCargandoEstudiantes
  ] = useState(false);


  // =======================================================
  // GENERACIÓN
  // =======================================================

  const [
    generando,
    setGenerando
  ] = useState(false);


  const [
    error,
    setError
  ] = useState("");


  const [
    resultado,
    setResultado
  ] = useState(null);

    const [
    progreso,
    setProgreso
  ] = useState({

    porcentaje: 0,

    procesados: 0,

    total: 0,

    tiempo_transcurrido: 0,

    eta_segundos: null,

    mensaje: "Preparando generación...",

  });

    function esperar(
    milisegundos
  ) {

    return new Promise(
      resolve =>
        setTimeout(
          resolve,
          milisegundos
        )
    );

  }


  // =======================================================
  // ANALIZAR EXCEL AUTOMÁTICAMENTE
  // =======================================================

  useEffect(() => {

    // Si no existe Excel,
    // limpiamos la vista previa.

    if (!excel) {

      setEstudiantes([]);

      setCantidadEstudiantes(0);

      return;

    }


    // La hoja debe tener nombre.

    if (!hoja.trim()) {

      setEstudiantes([]);

      setCantidadEstudiantes(0);

      return;

    }


    // Pequeño delay para evitar
    // peticiones mientras escribe.

    const timer = setTimeout(

      async () => {

        try {

          setCargandoEstudiantes(
            true
          );


          setError("");


          const resultado =
            await analizarExcel({

              excel,

              hoja,

              grado,

            });


          setEstudiantes(
            resultado.estudiantes
          );


          setCantidadEstudiantes(
            resultado.cantidad
          );


        } catch (error) {

          setEstudiantes([]);

          setCantidadEstudiantes(0);


          setError(
            error.message
            ||
            "No se pudo analizar el Excel."
          );


        } finally {

          setCargandoEstudiantes(
            false
          );

        }

      },

      500

    );


    return () =>
      clearTimeout(timer);


  }, [
    excel,
    hoja,
    grado,
  ]);


  // =======================================================
  // LIMPIAR RESULTADO ANTERIOR
  // =======================================================

  useEffect(() => {

    if (resultado?.url) {

      URL.revokeObjectURL(
        resultado.url
      );

    }


    setResultado(null);


  }, [
    plantilla,
    excel,
    fecha,
    evaluacion,
    grado,
    jornada,
    sesion,
    hoja,
  ]);


  // =======================================================
  // GENERAR PREMARCADO
  // =======================================================

  async function handleGenerar() {

  setError("");


  if (!plantilla) {

    setError(
      "Selecciona una plantilla PDF."
    );

    return;

  }


  if (!excel) {

    setError(
      "Selecciona el listado Excel."
    );

    return;

  }


  if (!evaluacion.trim()) {

    setError(
      "Escribe el nombre de la evaluación."
    );

    return;

  }


  try {

    setGenerando(true);


    setProgreso({

      porcentaje: 0,

      procesados: 0,

      total:
        cantidadEstudiantes,

      tiempo_transcurrido: 0,

      eta_segundos: null,

      mensaje:
        "Preparando generación...",

    });


    // =====================================================
    // INICIAR
    // =====================================================

    const inicio =
      await iniciarPremarcado({

        plantilla,

        excel,

        fecha,

        evaluacion,

        grado,

        jornada,

        sesion,

        hoja,

      });


    const jobId =
      inicio.job_id;


    // =====================================================
    // CONSULTAR PROGRESO
    // =====================================================

    while (true) {

      const estado =
        await obtenerEstadoPremarcado(
          jobId
        );


      setProgreso({

        porcentaje:
          estado.porcentaje ?? 0,

        procesados:
          estado.procesados ?? 0,

        total:
          estado.total ?? 0,

        tiempo_transcurrido:
          estado.tiempo_transcurrido ?? 0,

        eta_segundos:
          estado.eta_segundos,

        mensaje:
          estado.mensaje
          ||
          "Generando...",

      });


      // ===================================================
      // ERROR
      // ===================================================

      if (
        estado.estado
        === "error"
      ) {

        throw new Error(

          estado.error
          ||
          estado.mensaje
          ||
          "Error durante la generación."

        );

      }


      // ===================================================
      // COMPLETADO
      // ===================================================

      if (
        estado.estado
        === "completado"
      ) {

        const blob =
          await descargarPremarcado(
            jobId
          );


        const url =
          URL.createObjectURL(
            blob
          );


        setResultado({

          url,

          nombre:
            `Premarcado_${hoja}_${fecha}.pdf`,

        });


        break;

      }


      // Consultamos cada 500 ms

      await esperar(
        500
      );

    }


  } catch (error) {

    setError(

      error.message
      ||
      "No fue posible generar el premarcado."

    );


  } finally {

    setGenerando(false);

  }

}


  // =======================================================
  // UI
  // =======================================================

  return (

    <div className="page">


      {/* ================================================= */}
      {/* VOLVER */}
      {/* ================================================= */}

      <button

        className="back-button"

        onClick={() =>
          navigate("/")
        }

      >

        <ArrowLeft
          size={17}
        />

        Volver

      </button>


      {/* ================================================= */}
      {/* CABECERA */}
      {/* ================================================= */}

      <div className="page-header">

        <div>

          <span className="eyebrow">
            Módulo
          </span>


          <h1>
            Premarcado
          </h1>


          <p>

            Genera hojas de respuesta
            personalizadas a partir de una
            plantilla y un listado de estudiantes.

          </p>

        </div>


        <div className="header-status">

          <CheckCircle2
            size={18}
          />

          Motor VisionU listo

        </div>

      </div>


      {/* ================================================= */}
      {/* PASO 1 */}
      {/* ================================================= */}

      <section className="content-card">

        <div className="card-heading">

          <div className="step-number">
            1
          </div>


          <div>

            <h2>
              Archivos de entrada
            </h2>


            <p>
              Selecciona la plantilla y el listado.
            </p>

          </div>

        </div>


        <div className="upload-grid">


          {/* PDF */}

          <FileUpload

            title="Plantilla de respuestas"

            description={
              "Archivo PDF que será premarcado."
            }

            type="pdf"

            accept=".pdf"

            file={plantilla}

            onChange={
              setPlantilla
            }

          />


          {/* EXCEL */}

          <FileUpload

            title="Listado de estudiantes"

            description={
              "Archivo Excel con los estudiantes."
            }

            type="excel"

            accept=".xlsx,.xlsm"

            file={excel}

            onChange={
              setExcel
            }

          />


        </div>

      </section>


      {/* ================================================= */}
      {/* PASO 2 */}
      {/* ================================================= */}

      <section className="content-card">

        <div className="card-heading">

          <div className="step-number">
            2
          </div>


          <div>

            <h2>
              Información de la evaluación
            </h2>


            <p>
              Datos que aparecerán en cada hoja.
            </p>

          </div>

        </div>


        <div className="form-grid">


          {/* FECHA */}

          <label className="field">

            <span>
              Fecha
            </span>


            <input

              type="date"

              value={fecha}

              onChange={(event) =>
                setFecha(
                  event.target.value
                )
              }

            />

          </label>


          {/* EVALUACIÓN */}

          <label className="field">

            <span>
              Evaluación
            </span>


            <input

              type="text"

              placeholder="Ej. Indagar U01"

              value={evaluacion}

              onChange={(event) =>
                setEvaluacion(
                  event.target.value
                )
              }

            />

          </label>


          {/* HOJA */}

          <label className="field">

            <span>
              Hoja del Excel
            </span>


            <input

              type="text"

              placeholder="Ej. PU3"

              value={hoja}

              onChange={(event) =>
                setHoja(
                  event.target.value
                )
              }

            />

          </label>


          {/* GRADO */}

          <label className="field">

            <span>
              Grado
            </span>


            <select

              value={grado}

              onChange={(event) =>
                setGrado(
                  event.target.value
                )
              }

            >


              {Array.from(

                {
                  length: 11
                },

                (_, index) => (

                  <option

                    key={
                      index + 1
                    }

                    value={
                      String(
                        index + 1
                      )
                    }

                  >

                    {index + 1}

                  </option>

                )

              )}


            </select>

          </label>


          {/* JORNADA */}

          <label className="field">

            <span>
              Jornada
            </span>


            <select

              value={jornada}

              onChange={(event) =>
                setJornada(
                  event.target.value
                )
              }

            >

              <option value="Mañana">
                Mañana
              </option>


              <option value="Tarde">
                Tarde
              </option>

            </select>

          </label>


          {/* SESIÓN */}

          <label className="field">

            <span>
              Sesión
            </span>


            <select

              value={sesion}

              onChange={(event) =>
                setSesion(
                  event.target.value
                )
              }

            >

              <option value="1">
                Sesión 1
              </option>


              <option value="2">
                Sesión 2
              </option>

            </select>

          </label>


        </div>

      </section>


      {/* ================================================= */}
      {/* PASO 3 */}
      {/* ================================================= */}

      <section className="content-card">

        <div className="card-heading">

          <div className="step-number">
            3
          </div>


          <div>

            <h2>
              Estudiantes
            </h2>


            <p>
              Vista previa del listado cargado.
            </p>

          </div>

        </div>


        {/* CARGANDO */}

        {cargandoEstudiantes ? (

          <div className="empty-preview">

            <p>
              Analizando Excel...
            </p>

          </div>

        ) : (

          <>

            {/* CONTADOR */}

            {cantidadEstudiantes > 0 && (

              <div
                style={{
                  marginBottom: "14px",
                  color: "#66737d",
                  fontSize: "13px",
                }}
              >

                <strong
                  style={{
                    color: "#00425E",
                  }}
                >

                  {cantidadEstudiantes}

                </strong>

                {" "}

                estudiantes encontrados

              </div>

            )}


            {/* TABLA */}

            <StudentTable

              estudiantes={
                estudiantes
              }

            />

          </>

        )}

      </section>


      {/* ================================================= */}
      {/* GENERACIÓN */}
      {/* ================================================= */}

      <section className="generation-panel">


        <div className="generation-info">

          <div className="generation-icon">

            <Sparkles
              size={22}
            />

          </div>


          <div>

            <h3>
              Todo listo para generar
            </h3>


            <p>

              VisionU agregará encabezado,
              QR individual y guías OMR.

            </p>

          </div>

        </div>


        {/* ================================================= */}
        {/* RESUMEN */}
        {/* ================================================= */}

        <div className="summary-items">


          <div>

            <span>
              Plantilla
            </span>


            <strong>

              {
                plantilla
                  ? "Cargada"
                  : "Pendiente"
              }

            </strong>

          </div>


          <div>

            <span>
              Estudiantes
            </span>


            <strong>

              {
                cantidadEstudiantes
                  ? cantidadEstudiantes
                  : "—"
              }

            </strong>

          </div>


          <div>

            <span>
              Sesión
            </span>


            <strong>
              {sesion}
            </strong>

          </div>


        </div>


        {/* ================================================= */}
        {/* ERROR */}
        {/* ================================================= */}

        {error && (

          <div className="error-message">

            {error}

          </div>

        )}


        {/* ================================================= */}
        {/* GENERAR */}
        {/* ================================================= */}

        <button

          className="primary-button"

          onClick={
            handleGenerar
          }

          disabled={
            generando
            ||
            cargandoEstudiantes
          }

        >

          <FileText
            size={19}
          />


          {
            generando
              ? "Generando premarcado..."
              : "Generar premarcado"
          }

        </button>


        {/* ================================================= */}
        {/* DESCARGA */}
        {/* ================================================= */}

        {resultado && (

          <a

            className="download-button"

            href={
              resultado.url
            }

            download={
              resultado.nombre
            }

          >

            <Download
              size={19}
            />

            Descargar PDF generado

          </a>

        )}


      </section>

      {generando && (

  <div className="progress-overlay">


    <div className="progress-modal">


      <div className="progress-modal-header">

        <div className="progress-spinner">

          <Sparkles
            size={24}
          />

        </div>


        <div>

          <h2>
            Generando premarcado
          </h2>

          <p>
            {progreso.mensaje}
          </p>

        </div>

      </div>


      {/* BARRA */}

      <div className="progress-bar-container">

        <div
          className="progress-bar-fill"
          style={{
            width:
              `${progreso.porcentaje}%`
          }}
        />

      </div>


      {/* PORCENTAJE */}

      <div className="progress-percentage">

        <strong>

          {progreso.porcentaje}%

        </strong>

      </div>


      {/* DATOS */}

      <div className="progress-stats">


        <div>

          <span>
            Procesados
          </span>

          <strong>

            {progreso.procesados}
            {" / "}
            {progreso.total || cantidadEstudiantes}

          </strong>

        </div>


        <div>

          <span>
            Tiempo transcurrido
          </span>

          <strong>

            {progreso.tiempo_transcurrido}
            {" s"}

          </strong>

        </div>


        <div>

          <span>
            Tiempo estimado
          </span>

          <strong>

            {
              progreso.eta_segundos !== null

                ? `${progreso.eta_segundos} s`

                : "Calculando..."
            }

          </strong>

        </div>


      </div>


      <div className="progress-warning">

        No cierres esta ventana mientras
        VisionU genera las hojas.

      </div>


    </div>

  </div>

)}


    </div>

  );

}


export default Premarcado;