// =========================================================
// PROTECTED ROUTE - SGA PRO
// Archivo: frontend/src/components/ProtectedRoute.jsx
// Protege rutas por autenticación y roles.
// =========================================================

import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

function redirectByRole(rol) {
  if (rol === "ADMIN") return "/admin";
  if (rol === "COORDINADOR") return "/coordinador/dashboard";
  if (rol === "TECNICO") return "/tecnico";
  if (rol === "EMPRESA" || rol === "CLIENTE") return "/cliente/dashboard";
  return "/";
}

export default function ProtectedRoute({ allowedRoles = [], children }) {
  const { user, loadingSession } = useContext(AuthContext);

  if (loadingSession) {
    return <div style={{ padding: 32 }}>Validando sesión segura...</div>;
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.rol)) {
    return <Navigate to={redirectByRole(user.rol)} replace />;
  }

  return children;
}