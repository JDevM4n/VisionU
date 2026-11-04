import {
  useEffect,
  useState,
} from "react";

import {
  NavLink,
} from "react-router-dom";

import {
  Home,
  FileText,
  Library,
  ClipboardCheck,
  School,
  Circle,
} from "lucide-react";

import {
  verificarBackend,
} from "../services/api";


function Sidebar() {

  const [
    backendOnline,
    setBackendOnline
  ] = useState(false);


  useEffect(() => {

    async function comprobarBackend() {

      try {

        await verificarBackend();

        setBackendOnline(true);

      } catch {

        setBackendOnline(false);

      }

    }

    comprobarBackend();

  }, []);


  return (

    <aside className="sidebar">

      <div>

        {/* ================================================= */}
        {/* MARCA */}
        {/* ================================================= */}

        <div className="brand">

          <div className="brand-name">

            <span className="brand-vision">
              VISIÓN
            </span>

            <span className="brand-u">
              U
            </span>

          </div>

          <span className="brand-subtitle">
            Gestión de evaluaciones
          </span>

        </div>


        {/* ================================================= */}
        {/* MENÚ */}
        {/* ================================================= */}

        <nav className="sidebar-nav">

          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `nav-item ${
                isActive ? "nav-item-active" : ""
              }`
            }
          >

            <Home size={19} />

            <span>
              Inicio
            </span>

          </NavLink>


          <NavLink
            to="/premarcado"
            className={({ isActive }) =>
              `nav-item ${
                isActive ? "nav-item-active" : ""
              }`
            }
          >

            <FileText size={19} />

            <span>
              Premarcado
            </span>

          </NavLink>


          <button
            className="nav-item nav-item-disabled"
            disabled
          >

            <Library size={19} />

            <span>
              Biblioteca
            </span>

            <small>
              Próximamente
            </small>

          </button>


          <button
            className="nav-item nav-item-disabled"
            disabled
          >

            <ClipboardCheck size={19} />

            <span>
              Asistencia
            </span>

            <small>
              Próximamente
            </small>

          </button>


          <button
            className="nav-item nav-item-disabled"
            disabled
          >

            <School size={19} />

            <span>
              Salones
            </span>

            <small>
              Próximamente
            </small>

          </button>

        </nav>

      </div>


      {/* ================================================= */}
      {/* ESTADO BACKEND */}
      {/* ================================================= */}

      <div className="sidebar-footer">

        <div className="backend-status">

          <Circle
            size={9}
            fill={
              backendOnline
                ? "#84B541"
                : "#AEB8BF"
            }
            strokeWidth={0}
          />

          <span>

            {backendOnline
              ? "Sistema conectado"
              : "Backend desconectado"
            }

          </span>

        </div>

        <small>
          VisionU V2
        </small>

      </div>

    </aside>
  );
}

export default Sidebar;