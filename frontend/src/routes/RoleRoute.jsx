// ============================================================
// ROLE ROUTE PRO
// Archivo: frontend/src/routes/RoleRoute.jsx
// ============================================================
// Protege rutas por rol:
// ADMIN, COORDINADOR, CLIENTE, TECNICO
// ============================================================

import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function RoleRoute({ roles = [], children }) {
  const { loading, isAuthenticated, user } = useAuth();

  if (loading) {
    return (
      <div className="session-loading">
        <div className="session-loading-card">
          <div className="session-spinner" />
          <p>Validando rol del usuario...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const normalizedRoles = roles.map((r) => r.toUpperCase());
  const userRole = user?.rol?.toUpperCase();

  if (normalizedRoles.length > 0 && !normalizedRoles.includes(userRole)) {
    return <Navigate to="/no-autorizado" replace />;
  }

  return children || <Outlet />;
}
