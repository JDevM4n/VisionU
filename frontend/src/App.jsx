import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Home from "./pages/Home";
import Premarcado from "./pages/Premarcado";


function App() {
  return (
    <div className="app-shell">

      <Sidebar />

      <main className="main-content">

        <Routes>

          <Route
            path="/"
            element={<Home />}
          />

          <Route
            path="/premarcado"
            element={<Premarcado />}
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />

        </Routes>

      </main>

    </div>
  );
}

export default App;