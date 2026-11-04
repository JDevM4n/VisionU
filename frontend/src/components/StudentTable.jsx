import {
  useEffect,
  useState,
} from "react";

import {
  ChevronLeft,
  ChevronRight,
} from "lucide-react";


function StudentTable({
  estudiantes = [],
}) {

  const POR_PAGINA = 10;


  const [
    paginaActual,
    setPaginaActual
  ] = useState(1);


  // =======================================================
  // REINICIAR PÁGINA AL CAMBIAR EL EXCEL
  // =======================================================

  useEffect(() => {

    setPaginaActual(1);

  }, [estudiantes]);


  // =======================================================
  // SIN ESTUDIANTES
  // =======================================================

  if (!estudiantes.length) {

    return (

      <div className="empty-preview">

        La vista previa de los estudiantes
        aparecerá aquí cuando cargues un Excel.

      </div>

    );

  }


  // =======================================================
  // PAGINACIÓN
  // =======================================================

  const totalPaginas =
    Math.ceil(
      estudiantes.length / POR_PAGINA
    );


  const indiceInicio =
    (paginaActual - 1)
    * POR_PAGINA;


  const indiceFinal =
    indiceInicio
    + POR_PAGINA;


  const estudiantesPagina =
    estudiantes.slice(
      indiceInicio,
      indiceFinal
    );


  const irAnterior = () => {

    setPaginaActual(
      pagina =>
        Math.max(
          1,
          pagina - 1
        )
    );

  };


  const irSiguiente = () => {

    setPaginaActual(
      pagina =>
        Math.min(
          totalPaginas,
          pagina + 1
        )
    );

  };


  // =======================================================
  // UI
  // =======================================================

  return (

    <div className="student-table-wrapper">


      <div className="student-table-container">

        <table className="student-table">

          <thead>

            <tr>

              <th>
                Documento
              </th>

              <th>
                Nombre
              </th>

              <th>
                Grupo
              </th>

              <th>
                Grado
              </th>

              <th>
                Ciudad
              </th>

            </tr>

          </thead>


          <tbody>

            {estudiantesPagina.map(
              (
                estudiante,
                index
              ) => (

                <tr
                  key={
                    estudiante.documento
                    ||
                    `${paginaActual}-${index}`
                  }
                >

                  <td>
                    {
                      estudiante.documento
                    }
                  </td>


                  <td>
                    {
                      estudiante.nombre
                    }
                  </td>


                  <td>

                    <span className="group-badge">

                      {
                        estudiante.grupo
                      }

                    </span>

                  </td>


                  <td>
                    {
                      estudiante.grado
                    }
                  </td>


                  <td>
                    {
                      estudiante.ciudad
                    }
                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>

      </div>


      {/* ================================================= */}
      {/* PAGINACIÓN */}
      {/* ================================================= */}

      <div className="table-pagination">


        <div className="pagination-info">

          Mostrando

          {" "}

          <strong>
            {indiceInicio + 1}
          </strong>

          {" "}

          a

          {" "}

          <strong>
            {
              Math.min(
                indiceFinal,
                estudiantes.length
              )
            }
          </strong>

          {" "}

          de

          {" "}

          <strong>
            {estudiantes.length}
          </strong>

          {" "}

          estudiantes

        </div>


        <div className="pagination-controls">


          <button
            type="button"
            className="pagination-button"
            onClick={irAnterior}
            disabled={
              paginaActual === 1
            }
          >

            <ChevronLeft
              size={17}
            />

            Anterior

          </button>


          <span className="pagination-page">

            Página

            {" "}

            <strong>
              {paginaActual}
            </strong>

            {" "}

            de

            {" "}

            <strong>
              {totalPaginas}
            </strong>

          </span>


          <button
            type="button"
            className="pagination-button"
            onClick={irSiguiente}
            disabled={
              paginaActual === totalPaginas
            }
          >

            Siguiente

            <ChevronRight
              size={17}
            />

          </button>


        </div>

      </div>

    </div>

  );

}


export default StudentTable;