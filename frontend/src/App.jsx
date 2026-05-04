// =========================================================
// APP PRINCIPAL SGA PRO
// Define rutas principales del sistema
// =========================================================

import { BrowserRouter, Routes, Route } from "react-router-dom";

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

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<Login />} />

        {/* Dashboards */}
        <Route path="/admin" element={<DashboardAdmin />} />
        <Route path="/tecnico" element={<DashboardTecnico />} />

        {/* Rutas ADMIN */}
        <Route path="/admin/empresas" element={<EmpresasPage />} />
        <Route path="/admin/sedes" element={<SedesPage />} />
        <Route path="/admin/categorias" element={<CategoriasPage />} />
        <Route path="/admin/usuarios" element={<UsuariosPage />} />
        <Route path="/admin/tecnicos" element={<TecnicosPage />} />
        <Route path="/admin/equipos" element={<EquiposPage />} />
        <Route path="/admin/equipos/:equipoId/hoja-vida" element={<HojaVidaEquipoPage />} />
        <Route path="/admin/mantenimientos" element={<MantenimientosPage />} />
        <Route path="/admin/evidencias" element={<EvidenciasPage />} />
        <Route path="/admin/reportes" element={<ReportesPage />} />
        <Route path="/admin/configuracion" element={<ConfiguracionPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;