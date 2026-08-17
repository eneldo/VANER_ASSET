import { Navigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

const HOME_BY_ROLE = {
  ADMIN: "/admin/dashboard",
  COORDINADOR: "/coordinador/dashboard",
  TECNICO: "/tecnico/dashboard",
  EMPRESA: "/cliente/dashboard",
  CLIENTE: "/cliente/dashboard",
};

export default function RoleHomeRedirect() {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  const destination = HOME_BY_ROLE[String(user?.rol || "").toUpperCase()];
  return <Navigate to={destination || "/no-autorizado"} replace />;
}
