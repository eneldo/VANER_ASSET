// ============================================================
// AUTH CONTEXT PRO
// Archivo: frontend/src/context/AuthContext.jsx
// ============================================================
// Maneja sesión global del usuario:
// - login
// - logout
// - usuario autenticado
// - rol
// - empresa_id
// - permisos
// ============================================================

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../api/axios";
import {
  saveSession,
  clearSession,
  getStoredUser,
  getAccessToken,
  getRefreshToken,
} from "../utils/authStorage";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [loading, setLoading] = useState(true);

  // ==========================================================
  // Restaurar sesión local
  // ==========================================================

  useEffect(() => {
    const storedUser = getStoredUser();
    const token = getAccessToken();

    if (storedUser && token) {
      setUser(storedUser);
    }

    setLoading(false);
  }, []);

  // ==========================================================
  // LOGIN
  // ==========================================================

  const login = async ({ username, password }) => {
    const response = await api.post("/auth/login", {
      username,
      password,
    });

    const data = response.data;

    const loggedUser = {
      id: data.usuario_id,
      nombre_completo: data.nombre_completo,
      rol: data.rol,
      empresa_id: data.empresa_id || null,
      permisos: data.permisos || [],
    };

    saveSession({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      user: loggedUser,
    });

    setUser(loggedUser);

    return loggedUser;
  };

  // ==========================================================
  // LOGOUT
  // ==========================================================

  const logout = async () => {
    try {
      const refreshToken = getRefreshToken();

      if (refreshToken) {
        await api.post("/auth/logout", {
          refresh_token: refreshToken,
        });
      }
    } catch (error) {
      console.warn("Logout remoto no disponible o falló:", error);
    } finally {
      clearSession();
      setUser(null);
      window.location.href = "/login";
    }
  };

  // ==========================================================
  // HELPERS DE SEGURIDAD
  // ==========================================================

  const hasRole = (...roles) => {
    if (!user?.rol) return false;
    return roles.map((r) => r.toUpperCase()).includes(user.rol.toUpperCase());
  };

  const hasPermission = (permission) => {
    if (!permission) return true;

    // ADMIN siempre tiene acceso.
    if (user?.rol?.toUpperCase() === "ADMIN") return true;

    return Array.isArray(user?.permisos) && user.permisos.includes(permission);
  };

  const isAuthenticated = Boolean(user && getAccessToken());

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      logout,
      hasRole,
      hasPermission,
      isAuthenticated,
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }

  return context;
}
