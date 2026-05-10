// =========================================================
// APP PRINCIPAL SGA PRO
// Rutas protegidas por rol
// ADMIN / COORDINADOR / EMPRESA / TECNICO separados
// =========================================================

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
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
import AuditoriaPage from "./pages/admin/AuditoriaPage";
import ConfiguracionPage from "./pages/admin/ConfiguracionPage";

import ClienteLayout from "./pages/cliente/ClienteLayout";
import ClienteDashboard from "./pages/cliente/ClienteDashboard";
import ClienteSedes from "./pages/cliente/ClienteSedes";
import ClienteEquipos from "./pages/cliente/ClienteEquipos";
import ClienteMantenimientos from "./pages/cliente/ClienteMantenimientos";

import Sidebar from "./components/Sidebar";
import { AuthContext } from "./context/AuthContext";
import "./styles/sidebar.css";

// =========================================================
// Obtener usuario actual desde localStorage
// =========================================================

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("user"));
  } catch {
    return null;
  }
}

// =========================================================
// Redirección automática según rol
// =========================================================

function redirectByRole(rol) {
  if (rol === "ADMIN" || rol === "COORDINADOR") return "/admin";
  if (rol === "TECNICO") return "/tecnico";
  if (rol === "EMPRESA" || rol === "CLIENTE") return "/cliente/dashboard";
  return "/";
}

// =========================================================
// Ruta protegida por rol
// =========================================================

function RoleRoute({ allowedRoles, children }) {
  const user = getCurrentUser();

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (!allowedRoles.includes(user.rol)) {
    return <Navigate to={redirectByRole(user.rol)} replace />;
  }

  return children;
}

// =========================================================
// APP
// =========================================================

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<Login />} />

        {/* ADMIN / COORDINADOR */}
        <Route
          path="/admin"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <DashboardAdmin />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/dashboard"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <DashboardAdmin />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/empresas"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <EmpresasPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/sedes"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <SedesPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/categorias"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <CategoriasPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/usuarios"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <UsuariosPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/tecnicos"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <TecnicosPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/equipos"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <EquiposPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/equipos/:equipoId/hoja-vida"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <HojaVidaEquipoPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/mantenimientos"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <AdminShell>
                <MantenimientosPage />
              </AdminShell>
            </RoleRoute>
          }
        />

        <Route
          path="/admin/evidencias"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <EvidenciasPage />
            </RoleRoute>
          }
        />

        {/* FASE 26 - REPORTES PRO */}
        <Route
          path="/admin/reportes"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <ReportesPage />
            </RoleRoute>
          }
        />

        {/* FASE 26 - AUDITORÍA DEL SISTEMA */}
        <Route
          path="/admin/auditoria"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <AuditoriaPage />
            </RoleRoute>
          }
        />

        <Route
          path="/admin/configuracion"
          element={
            <RoleRoute allowedRoles={["ADMIN", "COORDINADOR"]}>
              <ConfiguracionPage />
            </RoleRoute>
          }
        />

        {/* TECNICO */}
        <Route
          path="/tecnico"
          element={
            <RoleRoute allowedRoles={["TECNICO"]}>
              <DashboardTecnico />
            </RoleRoute>
          }
        />

        {/* CLIENTE / EMPRESA */}
        <Route
          path="/cliente"
          element={
            <RoleRoute allowedRoles={["EMPRESA", "CLIENTE"]}>
              <ClienteLayout />
            </RoleRoute>
          }
        >
          <Route path="dashboard" element={<ClienteDashboard />} />
          <Route path="sedes" element={<ClienteSedes />} />
          <Route path="equipos" element={<ClienteEquipos />} />
          <Route path="mantenimientos" element={<ClienteMantenimientos />} />
          <Route path="cronograma" element={<ClienteMantenimientos />} />
        </Route>

        {/* Cualquier ruta no encontrada */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

// =========================================================
// Layout para páginas admin sin sidebar propio
// =========================================================

function AdminShell({ children }) {
  const { user, logout } = useContext(AuthContext);

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f5f8ff" }}>
      <Sidebar user={user} onLogout={logout} />

      <main
        style={{
          flex: 1,
          padding: "32px",
          overflowX: "hidden",

          // =====================================================
          // SCROLL VERTICAL PROFESIONAL
          // =====================================================
          height: "100vh",
          overflowY: "auto",
          paddingBottom: "120px",

          // Fondo institucional
          background: "#f5f8ff",
        }}
      >
        {children}
      </main>
    </div>
  );
}

export default App;