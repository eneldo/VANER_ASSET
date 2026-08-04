// ============================================================
// AUTH CONTEXT PRO
// Archivo: frontend/src/context/AuthContext.jsx
// ============================================================

import { useCallback, useMemo, useState } from "react";
import { AuthContext } from "./auth-context";
import api from "../api/axios";
import {
  saveSession,
  clearSession,
  getStoredUser,
  getAccessToken,
} from "../utils/authStorage";

function initialUser() {
  const storedUser = getStoredUser();
  if (storedUser && getAccessToken()) return storedUser;
  clearSession();
  return null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(initialUser);
  const loading = false;

  const login = async ({ username, password }) => {
    const response = await api.post("/auth/login", {
      username,
      password,
    });

    const data = response.data;

    const loggedUser = {
      id: data.usuario_id || data.id,
      nombre_completo: data.nombre_completo || data.nombre || "Usuario",
      username: data.username || username,
      email: data.email || username,
      rol: String(data.rol || "").toUpperCase(),
      empresa_id: data.empresa_id || null,
      permisos: data.permisos || [],
    };

    saveSession({
      access_token: data.access_token,
      user: loggedUser,
    });

    setUser(loggedUser);

    return loggedUser;
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout", {});
    } catch (error) {
      console.warn("Logout remoto no disponible o falló:", error);
    } finally {
      clearSession();
      setUser(null);
      window.location.href = "/";
    }
  };

  const hasRole = useCallback((...roles) => {
    if (!user?.rol) return false;
    return roles.map((r) => String(r).toUpperCase()).includes(user.rol);
  }, [user]);

  const hasPermission = useCallback((permission) => {
    if (!permission) return true;
    if (user?.rol === "ADMIN") return true;
    return Array.isArray(user?.permisos) && user.permisos.includes(permission);
  }, [user]);

  const isAuthenticated = Boolean(user && getAccessToken());

  const value = useMemo(
    () => ({
      user,
      loading,
      loadingSession: loading,
      login,
      logout,
      hasRole,
      hasPermission,
      isAuthenticated,
    }),
    [user, loading, hasRole, hasPermission, isAuthenticated]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
