// =========================================================
// APP PRINCIPAL SGA PRO - CORRECCIÓN FASES 27 A 31.2
// Archivo: frontend/src/App.jsx
//
// Objetivo de esta versión:
// - Restaurar rutas administrativas faltantes: Notificaciones,
//   Cronograma y Exportaciones.
// - Restaurar rutas del portal Cliente con layout anidado.
// - Evitar que un clic en Notificaciones caiga en path="*" y
//   devuelva al login.
// - Mantener ProtectedRoute basado en AuthContext/JWT.
// =========================================================

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

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
import AuditoriaPage from "./pages/admin/AuditoriaPage";
import ConfiguracionPage from "./pages/admin/ConfiguracionPage";
import ExportacionesPage from "./pages/admin/ExportacionesPage";
import CronogramaPage from "./pages/admin/CronogramaPage";
import NotificacionesPage from "./pages/admin/NotificacionesPage";

import ClienteLayout from "./pages/cliente/ClienteLayout";
import ClienteDashboard from "./pages/cliente/ClienteDashboard";
import ClienteSedes from "./pages/cliente/ClienteSedes";
import ClienteEquipos from "./pages/cliente/ClienteEquipos";
import ClienteMantenimientos from "./pages/cliente/ClienteMantenimientos";
import ClienteCronograma from "./pages/cliente/ClienteCronograma";
import ClienteNotificaciones from "./pages/cliente/ClienteNotificaciones";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";

import ProtectedRoute from "./components/ProtectedRoute";
import "./styles/sidebar.css";

const ADMIN_ROLES = ["ADMIN", "COORDINADOR"];
const CLIENTE_ROLES = ["EMPRESA", "CLIENTE"];
const TECNICO_ROLES = ["TECNICO"];

// =========================================================
// APP
// =========================================================
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* =================================================
            ADMIN / COORDINADOR
        ================================================= */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <DashboardAdmin />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <DashboardAdmin />
            </ProtectedRoute>
          }
        />

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
        <Route path="/admin/auditoria" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><AuditoriaPage /></ProtectedRoute>} />
        <Route path="/admin/configuracion" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ConfiguracionPage /></ProtectedRoute>} />

        {/* Fases recientes: estas rutas estaban faltando y causaban regreso al login */}
        <Route path="/admin/exportaciones" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ExportacionesPage /></ProtectedRoute>} />
        <Route path="/admin/cronograma" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><CronogramaPage /></ProtectedRoute>} />
        <Route path="/admin/notificaciones" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><NotificacionesPage /></ProtectedRoute>} />

        {/* =================================================
            TÉCNICO
        ================================================= */}
        <Route
          path="/tecnico"
          element={
            <ProtectedRoute allowedRoles={TECNICO_ROLES}>
              <DashboardTecnico />
            </ProtectedRoute>
          }
        />

        {/* =================================================
            PORTAL CLIENTE / EMPRESA
            Layout con rutas anidadas para que el sidebar del cliente
            permanezca fijo y solo cambie el contenido.
        ================================================= */}
        <Route
          path="/cliente"
          element={
            <ProtectedRoute allowedRoles={CLIENTE_ROLES}>
              <ClienteLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<ClienteDashboard />} />
          <Route path="sedes" element={<ClienteSedes />} />
          <Route path="equipos" element={<ClienteEquipos />} />
          <Route path="mantenimientos" element={<ClienteMantenimientos />} />
          <Route path="cronograma" element={<ClienteCronograma />} />
          <Route path="notificaciones" element={<ClienteNotificaciones />} />
        </Route>

        {/* Cualquier ruta desconocida vuelve al login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
