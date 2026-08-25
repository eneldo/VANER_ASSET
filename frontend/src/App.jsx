// =========================================================
// APP PRINCIPAL VANER ASSET
// Archivo: frontend/src/App.jsx
// Corregido según estructura real del proyecto
// =========================================================

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";

import ProtectedRoute from "./routes/ProtectedRoute";
import RoleRoute from "./routes/RoleRoute";
import RoleHomeRedirect from "./routes/RoleHomeRedirect";

// AUTH
const Login = lazy(() => import("./pages/Login"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));
const NoAutorizado = lazy(() => import("./pages/NoAutorizado"));

// DASHBOARDS REALES
const DashboardAdmin = lazy(() => import("./pages/DashboardAdmin"));
const DashboardTecnico = lazy(() => import("./pages/DashboardTecnico"));
const FormatoMantenimiento = lazy(() => import("./pages/tecnico/FormatoMantenimiento"));
const FormatoPrint = lazy(() => import("./pages/tecnico/FormatoPrint"));
const CoordinadorDashboard = lazy(() => import("./pages/coordinador/CoordinadorDashboard"));

// ADMIN
const EmpresasPage = lazy(() => import("./pages/admin/EmpresasPage"));
const SedesPage = lazy(() => import("./pages/admin/SedesPage"));
const CategoriasPage = lazy(() => import("./pages/admin/CategoriasPage"));
const TecnicosPage = lazy(() => import("./pages/admin/TecnicosPage"));
const UsuariosPage = lazy(() => import("./pages/admin/UsuariosPage"));
const EquiposPage = lazy(() => import("./pages/admin/EquiposPage"));
const HojaVidaEquipoPage = lazy(() => import("./pages/admin/HojaVidaEquipoPage"));
const MantenimientosPage = lazy(() => import("./pages/admin/MantenimientosPage"));
const EvidenciasPage = lazy(() => import("./pages/admin/EvidenciasPage"));
const ReportesPage = lazy(() => import("./pages/admin/ReportesPage"));
const AuditoriaPage = lazy(() => import("./pages/admin/AuditoriaPage"));
const ConfiguracionPage = lazy(() => import("./pages/admin/ConfiguracionPage"));
const ConfiguracionSistemaPage = lazy(() => import("./pages/admin/ConfiguracionSistemaPage"));
const AutomatizacionPage = lazy(() => import("./pages/admin/AutomatizacionPage"));
const BackupsInteligentesPage = lazy(() => import("./pages/admin/BackupsInteligentesPage"));
const SMTPInteligentePage = lazy(() => import("./pages/admin/SMTPInteligentePage"));
const MonitorVpsPage = lazy(() => import("./pages/admin/MonitorVpsPage"));
const LogsInteligentesPage = lazy(() => import("./pages/admin/LogsInteligentesPage"));
const DevOpsSaasPage = lazy(() => import("./pages/admin/DevOpsSaasPage"));
const SchedulerInteligentePage = lazy(() => import("./pages/admin/SchedulerInteligentePage"));
const RecoveryRestorePage = lazy(() => import("./pages/admin/RecoveryRestorePage"));
const MultiempresaEnterprisePage = lazy(() => import("./pages/admin/MultiempresaEnterprisePage"));
const BIExecutivePage = lazy(() => import("./pages/admin/BIExecutivePage"));
const FacturacionPage = lazy(() => import("./pages/admin/FacturacionPage"));
const PlantillasReportePage = lazy(() => import("./pages/admin/PlantillasReportePage"));

// CLIENTE
const ClienteLayout = lazy(() => import("./pages/cliente/ClienteLayout"));
const ClienteDashboard = lazy(() => import("./pages/cliente/ClienteDashboard"));
const ClienteSedes = lazy(() => import("./pages/cliente/ClienteSedes"));
const ClienteEquipos = lazy(() => import("./pages/cliente/ClienteEquipos"));
const ClienteMantenimientos = lazy(() => import("./pages/cliente/ClienteMantenimientos"));
const ClienteCronograma = lazy(() => import("./pages/cliente/ClienteCronograma"));
const ClienteSolicitudes = lazy(() => import("./pages/cliente/ClienteSolicitudes"));
const ClienteReportes = lazy(() => import("./pages/cliente/ClienteReportes"));

// COORDINADOR
const CoordinadorLayout = lazy(() => import("./layouts/CoordinadorLayout"));
const CoordinadorMantenimientos = lazy(() => import("./pages/coordinador/CoordinadorMantenimientos"));
const CoordinadorCronograma = lazy(() => import("./pages/coordinador/CoordinadorCronograma"));
const CoordinadorEquipos = lazy(() => import("./pages/coordinador/CoordinadorEquipos"));
const CoordinadorHojaVida = lazy(() => import("./pages/coordinador/CoordinadorHojaVida"));
const CoordinadorEvidencias = lazy(() => import("./pages/coordinador/CoordinadorEvidencias"));
const CoordinadorInformes = lazy(() => import("./pages/coordinador/CoordinadorInformes"));
const CoordinadorReportesPublicados = lazy(() => import("./pages/coordinador/CoordinadorReportesPublicados"));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="app-route-loading" role="status">Cargando módulo...</div>}>
      <Routes>
        {/* LOGIN */}
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/no-autorizado" element={<NoAutorizado />} />

        {/* ADMIN */}
        <Route element={<RoleRoute roles={["ADMIN"]} />}>
        <Route path="/admin/dashboard" element={<ProtectedRoute><DashboardAdmin /></ProtectedRoute>} />
        <Route path="/admin/empresas" element={<ProtectedRoute><EmpresasPage /></ProtectedRoute>} />
        <Route path="/admin/sedes" element={<ProtectedRoute><SedesPage /></ProtectedRoute>} />
        <Route path="/admin/categorias" element={<ProtectedRoute><CategoriasPage /></ProtectedRoute>} />
        <Route path="/admin/tecnicos" element={<ProtectedRoute><TecnicosPage /></ProtectedRoute>} />
        <Route path="/admin/usuarios" element={<ProtectedRoute><UsuariosPage /></ProtectedRoute>} />
        <Route path="/admin/equipos" element={<ProtectedRoute><EquiposPage /></ProtectedRoute>} />
        <Route path="/admin/inventarios" element={<ProtectedRoute><EquiposPage /></ProtectedRoute>} />
        <Route path="/admin/activos" element={<ProtectedRoute><EquiposPage /></ProtectedRoute>} />
        <Route path="/admin/hoja-vida/:id" element={<ProtectedRoute><HojaVidaEquipoPage /></ProtectedRoute>} />
        <Route path="/admin/mantenimientos" element={<ProtectedRoute><MantenimientosPage /></ProtectedRoute>} />
        <Route path="/admin/ordenes-trabajo" element={<ProtectedRoute><MantenimientosPage /></ProtectedRoute>} />
        <Route path="/admin/repuestos" element={<ProtectedRoute><MantenimientosPage /></ProtectedRoute>} />
        <Route path="/admin/evidencias" element={<ProtectedRoute><EvidenciasPage /></ProtectedRoute>} />
        <Route path="/admin/reportes" element={<ProtectedRoute><ReportesPage /></ProtectedRoute>} />
        <Route path="/admin/auditoria" element={<ProtectedRoute><AuditoriaPage /></ProtectedRoute>} />
        <Route path="/admin/bi-ejecutivo" element={<ProtectedRoute><BIExecutivePage /></ProtectedRoute>} />
        <Route path="/admin/facturacion" element={<ProtectedRoute><FacturacionPage /></ProtectedRoute>} />
        <Route path="/admin/plantillas-reportes" element={<ProtectedRoute><PlantillasReportePage /></ProtectedRoute>} />
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
        <Route path="/admin/multiempresa-enterprise" element={<ProtectedRoute><MultiempresaEnterprisePage /></ProtectedRoute>} />
        </Route>
        {/* TÉCNICO */}
        <Route element={<RoleRoute roles={["ADMIN", "TECNICO"]} />}>
        <Route path="/tecnico/dashboard" element={<ProtectedRoute><DashboardTecnico /></ProtectedRoute>} />
        <Route path="/tecnico/formato-mantenimiento/:mantenimientoId" element={<ProtectedRoute><FormatoMantenimiento /></ProtectedRoute>} />
        <Route path="/tecnico/formato-mantenimiento/:mantenimientoId/imprimir" element={<ProtectedRoute><FormatoPrint /></ProtectedRoute>} />
        </Route>

        {/* CLIENTE */}
        <Route path="/cliente" element={<RoleRoute roles={["ADMIN", "EMPRESA", "CLIENTE"]}><ClienteLayout /></RoleRoute>}>
          <Route path="dashboard" element={<ClienteDashboard />} />
          <Route path="sedes" element={<ClienteSedes />} />
          <Route path="equipos" element={<ClienteEquipos />} />
          <Route path="mantenimientos" element={<ClienteMantenimientos />} />
          <Route path="cronograma" element={<ClienteCronograma />} />
          <Route path="solicitudes" element={<ClienteSolicitudes />} />
          <Route path="reportes" element={<ClienteReportes />} />
        </Route>

        {/* COORDINADOR */}
        <Route path="/coordinador" element={<RoleRoute roles={["ADMIN", "COORDINADOR"]}><CoordinadorLayout /></RoleRoute>}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<CoordinadorDashboard />} />
          <Route path="mantenimientos" element={<CoordinadorMantenimientos />} />
          <Route path="cronograma" element={<CoordinadorCronograma />} />
          <Route path="equipos" element={<CoordinadorEquipos />} />
          <Route path="hoja-vida" element={<CoordinadorHojaVida />} />
          <Route path="hoja-vida/:equipoId" element={<CoordinadorHojaVida />} />
          <Route path="equipos/:equipoId/hoja-vida" element={<CoordinadorHojaVida />} />
          <Route path="evidencias" element={<CoordinadorEvidencias />} />
          <Route path="informes" element={<CoordinadorInformes />} />
          <Route path="reportes-publicados" element={<CoordinadorReportesPublicados />} />
        </Route>

        {/* FALLBACK */}
        <Route path="*" element={<RoleHomeRedirect />} />
      </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
