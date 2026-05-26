// =========================================================
// APP PRINCIPAL SGA SAAS PRO
// Archivo: frontend/src/App.jsx
// =========================================================

import { BrowserRouter, Routes, Route } from "react-router-dom";

import ProtectedRoute from "./routes/ProtectedRoute";

// =========================================================
// AUTH
// =========================================================

import Login from "./pages/Login";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";

// =========================================================
// DASHBOARDS
// =========================================================

import DashboardAdmin from "./pages/admin/DashboardAdmin";
import DashboardTecnico from "./pages/tecnico/DashboardTecnico";
import CoordinadorDashboard from "./pages/coordinador/CoordinadorDashboard";

// =========================================================
// ADMIN
// =========================================================

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

import ConfiguracionInteligentePage from "./pages/admin/ConfiguracionInteligentePage";
import ConfiguracionSistemaPage from "./pages/admin/ConfiguracionSistemaPage";

import AutomatizacionPage from "./pages/admin/AutomatizacionPage";
import BackupsInteligentesPage from "./pages/admin/BackupsInteligentesPage";
import SMTPInteligentePage from "./pages/admin/SMTPInteligentePage";

// =========================================================
// CLIENTE
// =========================================================

import ClienteLayout from "./pages/cliente/ClienteLayout";
import ClienteDashboard from "./pages/cliente/ClienteDashboard";
import ClienteSedes from "./pages/cliente/ClienteSedes";
import ClienteEquipos from "./pages/cliente/ClienteEquipos";
import ClienteMantenimientos from "./pages/cliente/ClienteMantenimientos";
import ClienteCronograma from "./pages/cliente/ClienteCronograma";

// =========================================================
// COORDINADOR
// =========================================================

import CoordinadorLayout from "./layouts/CoordinadorLayout";
import CoordinadorMantenimientos from "./pages/coordinador/CoordinadorMantenimientos";
import CoordinadorCronograma from "./pages/coordinador/CoordinadorCronograma";
import CoordinadorEquipos from "./pages/coordinador/CoordinadorEquipos";
import CoordinadorHojaVida from "./pages/coordinador/CoordinadorHojaVida";
import CoordinadorEvidencias from "./pages/coordinador/CoordinadorEvidencias";
import CoordinadorInformes from "./pages/coordinador/CoordinadorInformes";

// =========================================================
// ROLES
// =========================================================

const ADMIN_ROLES = ["ADMIN"];
const TECNICO_ROLES = ["TECNICO"];
const COORDINADOR_ROLES = ["COORDINADOR"];

// =========================================================
// APP
// =========================================================

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ================================================= */}
        {/* LOGIN */}
        {/* ================================================= */}

        <Route path="/" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />

        {/* ================================================= */}
        {/* ADMIN */}
        {/* ================================================= */}

        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <DashboardAdmin />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/empresas"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <EmpresasPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/sedes"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <SedesPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/categorias"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <CategoriasPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/tecnicos"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <TecnicosPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/usuarios"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <UsuariosPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/equipos"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <EquiposPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/hoja-vida/:id"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <HojaVidaEquipoPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/mantenimientos"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <MantenimientosPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/evidencias"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <EvidenciasPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/reportes"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <ReportesPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/auditoria"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <AuditoriaPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/configuracion"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <ConfiguracionPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/configuracion-inteligente"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <ConfiguracionInteligentePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/configuracion-sistema"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <ConfiguracionSistemaPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/automatizacion"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <AutomatizacionPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/backups"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <BackupsInteligentesPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/smtp-inteligente"
          element={
            <ProtectedRoute allowedRoles={ADMIN_ROLES}>
              <SMTPInteligentePage />
            </ProtectedRoute>
          }
        />

        {/* ================================================= */}
        {/* TÉCNICO */}
        {/* ================================================= */}

        <Route
          path="/tecnico/dashboard"
          element={
            <ProtectedRoute allowedRoles={TECNICO_ROLES}>
              <DashboardTecnico />
            </ProtectedRoute>
          }
        />

        {/* ================================================= */}
        {/* CLIENTE */}
        {/* ================================================= */}

        <Route
          path="/cliente"
          element={
            <ProtectedRoute>
              <ClienteLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<ClienteDashboard />} />
          <Route path="sedes" element={<ClienteSedes />} />
          <Route path="equipos" element={<ClienteEquipos />} />
          <Route path="mantenimientos" element={<ClienteMantenimientos />} />
          <Route path="cronograma" element={<ClienteCronograma />} />
        </Route>

        {/* ================================================= */}
        {/* COORDINADOR */}
        {/* ================================================= */}

        <Route
          path="/coordinador"
          element={
            <ProtectedRoute allowedRoles={COORDINADOR_ROLES}>
              <CoordinadorLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<CoordinadorDashboard />} />
          <Route path="mantenimientos" element={<CoordinadorMantenimientos />} />
          <Route path="cronograma" element={<CoordinadorCronograma />} />
          <Route path="equipos" element={<CoordinadorEquipos />} />
          <Route path="hoja-vida/:id" element={<CoordinadorHojaVida />} />
          <Route path="evidencias" element={<CoordinadorEvidencias />} />
          <Route path="informes" element={<CoordinadorInformes />} />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;