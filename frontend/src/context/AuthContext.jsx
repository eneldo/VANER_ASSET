// ============================================================
// AUTH CONTEXT PRO
// Archivo: frontend/src/context/AuthContext.jsx
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

  useEffect(() => {
    const storedUser = getStoredUser();
    const token = getAccessToken();

    if (storedUser && token) {
      setUser(storedUser);
    } else {
      clearSession();
      setUser(null);
    }

    setLoading(false);
  }, []);

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
      refresh_token: data.refresh_token,
      user: loggedUser,
    });

    setUser(loggedUser);

    return loggedUser;
  };

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
      window.location.href = "/";
    }
  };

  const hasRole = (...roles) => {
    if (!user?.rol) return false;
    return roles.map((r) => String(r).toUpperCase()).includes(user.rol);
  };

  const hasPermission = (permission) => {
    if (!permission) return true;
    if (user?.rol === "ADMIN") return true;
    return Array.isArray(user?.permisos) && user.permisos.includes(permission);
  };

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