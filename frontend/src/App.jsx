// =========================================================
// APP PRINCIPAL SGA PRO
// Archivo: frontend/src/App.jsx
// =========================================================

import { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLoader from "./components/AppLoader";
import "./styles/performance-pro.css";

const Login = lazy(() => import("./pages/Login"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));

const DashboardAdmin = lazy(() => import("./pages/DashboardAdmin"));
const EmpresasPage = lazy(() => import("./pages/admin/EmpresasPage"));
const SedesPage = lazy(() => import("./pages/admin/SedesPage"));
const CategoriasPage = lazy(() => import("./pages/admin/CategoriasPage"));
const UsuariosPage = lazy(() => import("./pages/admin/UsuariosPage"));
const TecnicosPage = lazy(() => import("./pages/admin/TecnicosPage"));
const EquiposPage = lazy(() => import("./pages/admin/EquiposPage"));
const HojaVidaEquipoPage = lazy(() => import("./pages/admin/HojaVidaEquipoPage"));
const MantenimientosPage = lazy(() => import("./pages/admin/MantenimientosPage"));
const EvidenciasPage = lazy(() => import("./pages/admin/EvidenciasPage"));
const ReportesPage = lazy(() => import("./pages/admin/ReportesPage"));
const AuditoriaPage = lazy(() => import("./pages/admin/AuditoriaPage"));
const ConfiguracionPage = lazy(() => import("./pages/admin/ConfiguracionPage"));

const DashboardTecnico = lazy(() => import("./pages/DashboardTecnico"));
const FormatoMantenimiento = lazy(() => import("./pages/tecnico/FormatoMantenimiento"));

const ClienteLayout = lazy(() => import("./pages/cliente/ClienteLayout"));
const ClienteDashboard = lazy(() => import("./pages/cliente/ClienteDashboard"));
const ClienteSedes = lazy(() => import("./pages/cliente/ClienteSedes"));
const ClienteEquipos = lazy(() => import("./pages/cliente/ClienteEquipos"));
const ClienteMantenimientos = lazy(() => import("./pages/cliente/ClienteMantenimientos"));
const ClienteCronograma = lazy(() => import("./pages/cliente/ClienteCronograma"));
const ClienteHojaVida = lazy(() => import("./pages/cliente/ClienteHojaVida"));

const CoordinadorLayout = lazy(() => import("./layouts/CoordinadorLayout"));
const CoordinadorDashboard = lazy(() => import("./pages/coordinador/CoordinadorDashboard"));
const CoordinadorMantenimientos = lazy(() => import("./pages/coordinador/CoordinadorMantenimientos"));
const CoordinadorCronograma = lazy(() => import("./pages/coordinador/CoordinadorCronograma"));
const CoordinadorEquipos = lazy(() => import("./pages/coordinador/CoordinadorEquipos"));
const CoordinadorHojaVida = lazy(() => import("./pages/coordinador/CoordinadorHojaVida"));
const CoordinadorEvidencias = lazy(() => import("./pages/coordinador/CoordinadorEvidencias"));
const CoordinadorInformes = lazy(() => import("./pages/coordinador/CoordinadorInformes"));

const ADMIN_ROLES = ["ADMIN"];
const TECNICO_ROLES = ["TECNICO"];
const CLIENTE_ROLES = ["EMPRESA", "CLIENTE"];
const COORDINADOR_ROLES = ["COORDINADOR", "ADMIN"];

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<AppLoader />}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><DashboardAdmin /></ProtectedRoute>} />
          <Route path="/admin/empresas" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><EmpresasPage /></ProtectedRoute>} />
          <Route path="/admin/sedes" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><SedesPage /></ProtectedRoute>} />
          <Route path="/admin/categorias" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><CategoriasPage /></ProtectedRoute>} />
          <Route path="/admin/usuarios" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><UsuariosPage /></ProtectedRoute>} />
          <Route path="/admin/tecnicos" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><TecnicosPage /></ProtectedRoute>} />
          <Route path="/admin/configuracion" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ConfiguracionPage /></ProtectedRoute>} />
          <Route path="/admin/configuracion-inteligente" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ConfiguracionPage /></ProtectedRoute>} />
          <Route path="/admin/equipos" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><EquiposPage /></ProtectedRoute>} />
          <Route path="/admin/equipos/:equipoId/hoja-vida" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><HojaVidaEquipoPage /></ProtectedRoute>} />
          <Route path="/admin/mantenimientos" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><MantenimientosPage /></ProtectedRoute>} />
          <Route path="/admin/evidencias" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><EvidenciasPage /></ProtectedRoute>} />
          <Route path="/admin/reportes" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><ReportesPage /></ProtectedRoute>} />
          <Route path="/admin/auditoria" element={<ProtectedRoute allowedRoles={ADMIN_ROLES}><AuditoriaPage /></ProtectedRoute>} />

          <Route path="/tecnico/dashboard" element={<ProtectedRoute allowedRoles={TECNICO_ROLES}><DashboardTecnico /></ProtectedRoute>} />
          <Route path="/tecnico/formato-mantenimiento/:mantenimientoId" element={<ProtectedRoute allowedRoles={TECNICO_ROLES}><FormatoMantenimiento /></ProtectedRoute>} />

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

          <Route path="/coordinador" element={<ProtectedRoute allowedRoles={COORDINADOR_ROLES}><CoordinadorLayout /></ProtectedRoute>}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<CoordinadorDashboard />} />
            <Route path="mantenimientos" element={<CoordinadorMantenimientos />} />
            <Route path="cronograma" element={<CoordinadorCronograma />} />
            <Route path="equipos" element={<CoordinadorEquipos />} />
            <Route path="equipos/:equipoId/hoja-vida" element={<CoordinadorHojaVida />} />
            <Route path="hoja-vida" element={<CoordinadorHojaVida />} />
            <Route path="evidencias" element={<CoordinadorEvidencias />} />
            <Route path="informes" element={<CoordinadorInformes />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
