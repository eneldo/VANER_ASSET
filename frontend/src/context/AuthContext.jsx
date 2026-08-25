import { useCallback, useEffect, useMemo, useState } from "react";

import api from "../api/axios";
import { AuthContext } from "./auth-context";
import {
  clearSession,
  getAccessToken,
  saveSession,
  updateAccessToken,
} from "../utils/authStorage";


function normalizarUsuario(data, fallbackUsername = "") {
  return {
    id: data.usuario_id || data.id,
    nombre_completo: data.nombre_completo || data.nombre || "Usuario",
    username: data.username || fallbackUsername,
    email: data.email || fallbackUsername,
    rol: String(data.rol || "").toUpperCase(),
    empresa_id: data.empresa_id || null,
    empresa_ids: data.empresa_ids || (data.empresa_id ? [data.empresa_id] : []),
    permisos: data.permisos || [],
  };
}


export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    let active = true;

    async function bootstrapSession() {
      try {
        const refreshResponse = await api.post("/auth/refresh", {});
        const accessToken = refreshResponse.data.access_token;
        updateAccessToken(accessToken);

        const meResponse = await api.get("/auth/me");
        const sessionUser = normalizarUsuario({
          ...refreshResponse.data,
          ...meResponse.data,
        });

        saveSession({ access_token: accessToken, user: sessionUser });
        if (active) {
          setUser(sessionUser);
          setAuthenticated(true);
        }
      } catch {
        clearSession();
        if (active) {
          setUser(null);
          setAuthenticated(false);
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    bootstrapSession();
    return () => {
      active = false;
    };
  }, []);

  const login = async ({ username, password }) => {
    const response = await api.post("/auth/login", { username, password });
    const loggedUser = normalizarUsuario(response.data, username);

    saveSession({
      access_token: response.data.access_token,
      user: loggedUser,
    });
    setUser(loggedUser);
    setAuthenticated(true);
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
      setAuthenticated(false);
      window.location.href = "/";
    }
  };

  const hasRole = useCallback((...roles) => {
    if (!user?.rol) return false;
    return roles.map((role) => String(role).toUpperCase()).includes(user.rol);
  }, [user]);

  const hasPermission = useCallback((permission) => {
    if (!permission) return true;
    if (user?.rol === "ADMIN") return true;
    return Array.isArray(user?.permisos) && user.permisos.includes(permission);
  }, [user]);

  const isAuthenticated = authenticated && Boolean(user && getAccessToken());
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
    [user, loading, hasRole, hasPermission, isAuthenticated],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
