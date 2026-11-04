import {
  useNavigate,
} from "react-router-dom";

import {
  FileText,
  ClipboardCheck,
  School,
  ArrowRight,
  Library,
} from "lucide-react";


function Home() {

  const navigate =
    useNavigate();


  return (

    <div className="page">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div className="page-header">

        <div>

          <span className="eyebrow">
            Plataforma VisionU
          </span>

          <h1>
            Gestión de evaluaciones
          </h1>

          <p>
            Centraliza la preparación,
            organización y procesamiento
            de tus jornadas académicas.
          </p>

        </div>

      </div>


      {/* ================================================= */}
      {/* BIENVENIDA */}
      {/* ================================================= */}

      <section className="welcome-panel">

        <div>

          <span className="welcome-label">
            VISION U
          </span>

          <h2>
            ¿Qué necesitas hacer hoy?
          </h2>

          <p>

            Selecciona uno de los módulos
            disponibles para comenzar.

          </p>

        </div>

        <div className="welcome-decoration">

          <span />
          <span />
          <span />

        </div>

      </section>


      {/* ================================================= */}
      {/* MÓDULOS */}
      {/* ================================================= */}

      <div className="section-title-row">

        <div>

          <h2>
            Módulos
          </h2>

          <p>
            Herramientas disponibles en VisionU.
          </p>

        </div>

      </div>


      <div className="modules-grid">

        {/* PREMARCADO */}

        <article
          className="module-card module-card-active"
          onClick={() =>
            navigate("/premarcado")
          }
        >

          <div className="module-icon">

            <FileText size={25} />

          </div>

          <div className="module-card-body">

            <div className="module-title-row">

              <h3>
                Premarcado
              </h3>

              <span className="status-badge">
                Disponible
              </span>

            </div>

            <p>

              Genera hojas personalizadas
              desde Excel con QR y guías OMR
              automáticas.

            </p>

          </div>

          <div className="module-footer">

            <span>
              Abrir módulo
            </span>

            <ArrowRight size={18} />

          </div>

        </article>


        {/* BIBLIOTECA */}

        <article className="module-card module-card-disabled">

          <div className="module-icon module-icon-muted">

            <Library size={25} />

          </div>

          <div className="module-card-body">

            <h3>
              Biblioteca
            </h3>

            <p>

              Reutiliza plantillas PDF
              y listados de estudiantes.

            </p>

          </div>

          <span className="coming-soon">
            Próximamente
          </span>

        </article>


        {/* ASISTENCIA */}

        <article className="module-card module-card-disabled">

          <div className="module-icon module-icon-muted">

            <ClipboardCheck size={25} />

          </div>

          <div className="module-card-body">

            <h3>
              Asistencia
            </h3>

            <p>

              Administra asistencia,
              horarios y bloques de aplicación.

            </p>

          </div>

          <span className="coming-soon">
            Próximamente
          </span>

        </article>


        {/* SALONES */}

        <article className="module-card module-card-disabled">

          <div className="module-icon module-icon-muted">

            <School size={25} />

          </div>

          <div className="module-card-body">

            <h3>
              Salones
            </h3>

            <p>

              Distribuye estudiantes
              automáticamente por salón.

            </p>

          </div>

          <span className="coming-soon">
            Próximamente
          </span>

        </article>

      </div>

    </div>
  );
}

export default Home;