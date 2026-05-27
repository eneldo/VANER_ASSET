// =========================================================
// APP PRINCIPAL SGA SAAS PRO
// Archivo: frontend/src/App.jsx
// Corregido según estructura real del proyecto
// =========================================================

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import ProtectedRoute from "./routes/ProtectedRoute";

// AUTH
import Login from "./pages/Login";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import NoAutorizado from "./pages/NoAutorizado";

// DASHBOARDS REALES
import DashboardAdmin from "./pages/DashboardAdmin";
import DashboardTecnico from "./pages/DashboardTecnico";
import CoordinadorDashboard from "./pages/coordinador/CoordinadorDashboard";

// ADMIN
import EmpresasPage from "./pages/admin/EmpresasPage";
import SedesPage from "./pages/admin/SedesPage";
import CategoriasPage from "./pages/admin/CategoriasPage";
import TecnicosPage from "./pages/admin/TecnicosPage";
import UsuariosPage from "./pages/admin/UsuariosPage";
import EquiposPage from "./pages/admin/EquiposPage";
import HojaVidaEquipoPage from "./pages/admin/HojaVidaEquipoPage";
import MantenimientosPage from "./pages/admin/MantenimientosPage";
import EvidenciasPage from "./pages/admin/EvidenciasPage";
import ReportesPage from "./pages/admin/ReportesPage";
import AuditoriaPage from "./pages/admin/AuditoriaPage";
import ConfiguracionPage from "./pages/admin/ConfiguracionPage";
import ConfiguracionSistemaPage from "./pages/admin/ConfiguracionSistemaPage";
import AutomatizacionPage from "./pages/admin/AutomatizacionPage";
import BackupsInteligentesPage from "./pages/admin/BackupsInteligentesPage";
import SMTPInteligentePage from "./pages/admin/SMTPInteligentePage";
import MonitorVpsPage from "./pages/admin/MonitorVpsPage";
import LogsInteligentesPage from "./pages/admin/LogsInteligentesPage";
import DevOpsSaasPage from "./pages/admin/DevOpsSaasPage";
import SchedulerInteligentePage from "./pages/admin/SchedulerInteligentePage";
import RecoveryRestorePage from "./pages/admin/RecoveryRestorePage";

// CLIENTE
import ClienteLayout from "./pages/cliente/ClienteLayout";
import ClienteDashboard from "./pages/cliente/ClienteDashboard";
import ClienteSedes from "./pages/cliente/ClienteSedes";
import ClienteEquipos from "./pages/cliente/ClienteEquipos";
import ClienteMantenimientos from "./pages/cliente/ClienteMantenimientos";
import ClienteCronograma from "./pages/cliente/ClienteCronograma";

// COORDINADOR
import CoordinadorLayout from "./layouts/CoordinadorLayout";
import CoordinadorMantenimientos from "./pages/coordinador/CoordinadorMantenimientos";
import CoordinadorCronograma from "./pages/coordinador/CoordinadorCronograma";
import CoordinadorEquipos from "./pages/coordinador/CoordinadorEquipos";
import CoordinadorHojaVida from "./pages/coordinador/CoordinadorHojaVida";
import CoordinadorEvidencias from "./pages/coordinador/CoordinadorEvidencias";
import CoordinadorInformes from "./pages/coordinador/CoordinadorInformes";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* LOGIN */}
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />
        <Route path="/no-autorizado" element={<NoAutorizado />} />

        {/* ADMIN */}
        <Route path="/admin/dashboard" element={<ProtectedRoute><DashboardAdmin /></ProtectedRoute>} />
        <Route path="/admin/empresas" element={<ProtectedRoute><EmpresasPage /></ProtectedRoute>} />
        <Route path="/admin/sedes" element={<ProtectedRoute><SedesPage /></ProtectedRoute>} />
        <Route path="/admin/categorias" element={<ProtectedRoute><CategoriasPage /></ProtectedRoute>} />
        <Route path="/admin/tecnicos" element={<ProtectedRoute><TecnicosPage /></ProtectedRoute>} />
        <Route path="/admin/usuarios" element={<ProtectedRoute><UsuariosPage /></ProtectedRoute>} />
        <Route path="/admin/equipos" element={<ProtectedRoute><EquiposPage /></ProtectedRoute>} />
        <Route path="/admin/hoja-vida/:id" element={<ProtectedRoute><HojaVidaEquipoPage /></ProtectedRoute>} />
        <Route path="/admin/mantenimientos" element={<ProtectedRoute><MantenimientosPage /></ProtectedRoute>} />
        <Route path="/admin/evidencias" element={<ProtectedRoute><EvidenciasPage /></ProtectedRoute>} />
        <Route path="/admin/reportes" element={<ProtectedRoute><ReportesPage /></ProtectedRoute>} />
        <Route path="/admin/auditoria" element={<ProtectedRoute><AuditoriaPage /></ProtectedRoute>} />

        <Route path="/admin/configuracion" element={<ProtectedRoute><ConfiguracionPage /></ProtectedRoute>} />
        <Route path="/admin/configuracion-inteligente" element={<ProtectedRoute><ConfiguracionPage /></ProtectedRoute>} />
        <Route path="/admin/configuracion-sistema" element={<ProtectedRoute><ConfiguracionSistemaPage /></ProtectedRoute>} />

        <Route path="/admin/automatizacion" element={<ProtectedRoute><AutomatizacionPage /></ProtectedRoute>} />
        <Route path="/admin/backups" element={<ProtectedRoute><BackupsInteligentesPage /></ProtectedRoute>} />
        <Route path="/admin/smtp-inteligente" element={<ProtectedRoute><SMTPInteligentePage /></ProtectedRoute>} />
        <Route path="/admin/monitor-vps" element={<ProtectedRoute><MonitorVpsPage /></ProtectedRoute>} />
        <Route path="/admin/logs-inteligentes" element={<ProtectedRoute><LogsInteligentesPage /></ProtectedRoute>} />
        <Route path="/admin/devops" element={<ProtectedRoute><DevOpsSaasPage /></ProtectedRoute>} />
        <Route path="/admin/scheduler-inteligente" element={<ProtectedRoute><SchedulerInteligentePage /></ProtectedRoute>} />
        <Route path="/admin/recovery" element={<ProtectedRoute><RecoveryRestorePage /></ProtectedRoute>} />
        {/* TÉCNICO */}
        <Route path="/tecnico/dashboard" element={<ProtectedRoute><DashboardTecnico /></ProtectedRoute>} />

        {/* CLIENTE */}
        <Route path="/cliente" element={<ProtectedRoute><ClienteLayout /></ProtectedRoute>}>
          <Route path="dashboard" element={<ClienteDashboard />} />
          <Route path="sedes" element={<ClienteSedes />} />
          <Route path="equipos" element={<ClienteEquipos />} />
          <Route path="mantenimientos" element={<ClienteMantenimientos />} />
          <Route path="cronograma" element={<ClienteCronograma />} />
        </Route>

        {/* COORDINADOR */}
        <Route path="/coordinador" element={<ProtectedRoute><CoordinadorLayout /></ProtectedRoute>}>
          <Route path="dashboard" element={<CoordinadorDashboard />} />
          <Route path="mantenimientos" element={<CoordinadorMantenimientos />} />
          <Route path="cronograma" element={<CoordinadorCronograma />} />
          <Route path="equipos" element={<CoordinadorEquipos />} />
          <Route path="hoja-vida/:id" element={<CoordinadorHojaVida />} />
          <Route path="evidencias" element={<CoordinadorEvidencias />} />
          <Route path="informes" element={<CoordinadorInformes />} />
        </Route>

        {/* FALLBACK */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;