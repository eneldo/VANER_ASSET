// ============================================================
// PROTECTED ROUTE PRO
// Archivo: frontend/src/routes/ProtectedRoute.jsx
// ============================================================
// Protege rutas por:
// - sesión activa
// - permisos opcionales
// ============================================================

import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function ProtectedRoute({ permission, children }) {
  const { loading, isAuthenticated, hasPermission } = useAuth();

  if (loading) {
    return (
      <div className="session-loading">
        <div className="session-loading-card">
          <div className="session-spinner" />
          <p>Validando sesión segura...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (permission && !hasPermission(permission)) {
    return <Navigate to="/no-autorizado" replace />;
  }

  return children || <Outlet />;
}
