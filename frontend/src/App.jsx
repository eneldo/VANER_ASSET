// =========================================================
// APP PRINCIPAL SGA PRO
// Define rutas principales del sistema
// =========================================================

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useContext } from "react";

import Login from "./pages/Login";
import DashboardTecnico from "./pages/DashboardTecnico";
import DashboardAdmin from "./pages/DashboardAdmin";

import EmpresasPage from "./pages/admin/EmpresasPage";
import SedesPage from "./pages/admin/SedesPage";
import CategoriasPage from "./pages/admin/CategoriasPage";
import UsuariosPage from "./pages/admin/UsuariosPage";
import TecnicosPage from "./pages/admin/TecnicosPage";
import EquiposPage from "./pages/admin/EquiposPage";
import HojaVidaEquipoPage from "./pages/admin/HojaVidaEquipoPage";
import MantenimientosPage from "./pages/admin/MantenimientosPage";
import EvidenciasPage from "./pages/admin/EvidenciasPage";
import ReportesPage from "./pages/admin/ReportesPage";
import ConfiguracionPage from "./pages/admin/ConfiguracionPage";

import Sidebar from "./components/Sidebar";
import { AuthContext } from "./context/AuthContext";
import "./styles/sidebar.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<Login />} />

        {/* Dashboards */}
        <Route path="/admin" element={<DashboardAdmin />} />
        <Route path="/admin/dashboard" element={<DashboardAdmin />} />
        <Route path="/tecnico" element={<DashboardTecnico />} />

        {/* Rutas ADMIN existentes: se dejan directas porque ya tienen su layout */}
        <Route path="/admin/empresas" element={<EmpresasPage />} />
        <Route path="/admin/sedes" element={<SedesPage />} />
        <Route path="/admin/categorias" element={<CategoriasPage />} />
        <Route path="/admin/usuarios" element={<UsuariosPage />} />
        <Route path="/admin/tecnicos" element={<TecnicosPage />} />
        <Route path="/admin/equipos" element={<EquiposPage />} />
        <Route path="/admin/equipos/:equipoId/hoja-vida" element={<HojaVidaEquipoPage />} />

        {/* Solo Mantenimientos va envuelto porque el nuevo diseño no trae sidebar propio */}
        <Route
          path="/admin/mantenimientos"
          element={
            <AdminShell>
              <MantenimientosPage />
            </AdminShell>
          }
        />

        <Route path="/admin/evidencias" element={<EvidenciasPage />} />
        <Route path="/admin/reportes" element={<ReportesPage />} />
        <Route path="/admin/configuracion" element={<ConfiguracionPage />} />
      </Routes>
    </BrowserRouter>
  );
}

// =========================================================
// Layout solo para páginas que NO tienen sidebar propio
// =========================================================

function AdminShell({ children }) {
  const { user, logout } = useContext(AuthContext);

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f5f8ff" }}>
      <Sidebar user={user} onLogout={logout} />

      <main style={{ flex: 1, padding: "32px", overflowX: "hidden" }}>
        {children}
      </main>
    </div>
  );
}

export default App;