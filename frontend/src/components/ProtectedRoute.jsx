// =========================================================
// PROTECTED ROUTE - SGAHolding
// Archivo: frontend/src/components/ProtectedRoute.jsx
// =========================================================

import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/auth-context";

function redirectByRole(rol) {
  const role = String(rol || "").toUpperCase();

  if (role === "ADMIN") return "/admin/dashboard";
  if (role === "COORDINADOR") return "/coordinador/dashboard";
  if (role === "TECNICO") return "/tecnico/dashboard";
  if (role === "EMPRESA" || role === "CLIENTE") return "/cliente/dashboard";

  return "/";
}

export default function ProtectedRoute({ allowedRoles = [], children }) {
  const { user, loading, isAuthenticated } = useContext(AuthContext);

  if (loading) {
    return <div style={{ padding: 32 }}>Validando sesión segura...</div>;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/" replace />;
  }

  const userRole = String(user.rol || "").toUpperCase();
  const rolesPermitidos = allowedRoles.map((r) => String(r).toUpperCase());

  if (rolesPermitidos.length > 0 && !rolesPermitidos.includes(userRole)) {
    return <Navigate to={redirectByRole(userRole)} replace />;
  }

  return children;
}
