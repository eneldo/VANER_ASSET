// =========================================================
// APP PRINCIPAL SGA PRO - RESPONSIVE PRO
// Archivo: frontend/src/App.jsx
// Fase 32.2
// =========================================================

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import ProtectedRoute from "./components/ProtectedRoute";

// ADMIN
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

// TÉCNICO
import DashboardTecnico from "./pages/DashboardTecnico";
import FormatoMantenimiento from "./pages/tecnico/FormatoMantenimiento";

// CLIENTE
import ClienteLayout from "./pages/cliente/ClienteLayout";
import ClienteDashboard from "./pages/cliente/ClienteDashboard";
import ClienteSedes from "./pages/cliente/ClienteSedes";
import ClienteEquipos from "./pages/cliente/ClienteEquipos";
import ClienteMantenimientos from "./pages/cliente/ClienteMantenimientos";
import ClienteCronograma from "./pages/cliente/ClienteCronograma";
import ClienteHojaVida from "./pages/cliente/ClienteHojaVida";

// COORDINADOR
import CoordinadorLayout from "./layouts/CoordinadorLayout";
import CoordinadorDashboard from "./pages/coordinador/CoordinadorDashboard";

import "./styles/responsive-pro.css";

const ADMIN_ROLES = ["ADMIN"];
const TECNICO_ROLES = ["TECNICO"];
const CLIENTE_ROLES = ["EMPRESA", "CLIENTE"];
const COORDINADOR_ROLES = ["COORDINADOR", "ADMIN"];

function ModuloNoDisponible({ titulo = "Módulo en construcción" }) {
  return (
    <div className="page-card empty-module-card">
      <h2>{titulo}</h2>
      <p>
        Esta ruta ya quedó protegida y preparada. En la siguiente fase conectamos
        el componente funcional correspondiente sin romper navegación.
      </p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* PÚBLICAS */}
        <Route path="/" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* ADMIN */}
        <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><DashboardAdmin /></ProtectedRoute>} />
        <Route path="/admin/empresas" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><EmpresasPage /></ProtectedRoute>} />
        <Route path="/admin/sedes" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><SedesPage /></ProtectedRoute>} />
        <Route path="/admin/categorias" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><CategoriasPage /></ProtectedRoute>} />
        <Route path="/admin/usuarios" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><UsuariosPage /></ProtectedRoute>} />
        <Route path="/admin/tecnicos" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><TecnicosPage /></ProtectedRoute>} />
        <Route path="/admin/equipos" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><EquiposPage /></ProtectedRoute>} />
        <Route path="/admin/equipos/:equipoId/hoja-vida" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><HojaVidaEquipoPage /></ProtectedRoute>} />
        <Route path="/admin/mantenimientos" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><MantenimientosPage /></ProtectedRoute>} />
        <Route path="/admin/evidencias" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><EvidenciasPage /></ProtectedRoute>} />
        <Route path="/admin/reportes" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ReportesPage /></ProtectedRoute>} />
        <Route path="/admin/auditoria" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ModuloNoDisponible titulo="Auditoría PRO" /></ProtectedRoute>} />
        <Route path="/admin/configuracion" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ModuloNoDisponible titulo="Configuración PRO" /></ProtectedRoute>} />

        {/* TÉCNICO */}
        <Route path="/tecnico/dashboard" element={<ProtectedRoute allowedRoles={TECNICO_ROLES}><DashboardTecnico /></ProtectedRoute>} />
        <Route path="/tecnico/mantenimientos" element={<Navigate to="/tecnico/dashboard" replace />} />
        <Route path="/tecnico/evidencias" element={<Navigate to="/tecnico/dashboard" replace />} />
        <Route path="/tecnico/formato-mantenimiento/:mantenimientoId" element={<ProtectedRoute allowedRoles={TECNICO_ROLES}><FormatoMantenimiento /></ProtectedRoute>} />

        {/* CLIENTE */}
        <Route path="/cliente" element={<ProtectedRoute allowedRoles={CLIENTE_ROLES}><ClienteLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<ClienteDashboard />} />
          <Route path="sedes" element={<ClienteSedes />} />
          <Route path="equipos" element={<ClienteEquipos />} />
          <Route path="equipos/:equipoId/hoja-vida" element={<ClienteHojaVida />} />
          <Route path="hoja-vida/:equipoId" element={<ClienteHojaVida />} />
          <Route path="mantenimientos" element={<ClienteMantenimientos />} />
          <Route path="cronograma" element={<ClienteCronograma />} />
        </Route>

        {/* COORDINADOR */}
        <Route path="/coordinador" element={<ProtectedRoute allowedRoles={COORDINADOR_ROLES}><CoordinadorLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<CoordinadorDashboard />} />
          <Route path="mantenimientos" element={<ModuloNoDisponible titulo="Mantenimientos Coordinador" />} />
          <Route path="cronograma" element={<ModuloNoDisponible titulo="Cronograma Coordinador" />} />
          <Route path="equipos" element={<ModuloNoDisponible titulo="Inventario / Equipos Coordinador" />} />
          <Route path="evidencias" element={<ModuloNoDisponible titulo="Evidencias Coordinador" />} />
          <Route path="hoja-vida" element={<ModuloNoDisponible titulo="Hoja de vida Coordinador" />} />
          <Route path="informes" element={<ModuloNoDisponible titulo="Informes Coordinador" />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
