// ============================================================
// AXIOS PRO CON REFRESH TOKEN AUTOMÁTICO
// Archivo: frontend/src/api/axios.js
//
// Corrige:
// - Compatible con token/access_token.
// - Compatible con refresh_token.
// - Evita redirigir a /login si tu login está en /.
// - Usa /auth/refresh, ahora existente en backend.
// ============================================================

import axios from "axios";
import {
  getAccessToken,
  getRefreshToken,
  updateAccessToken,
  updateRefreshToken,
  clearSession,
} from "../utils/authStorage";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token);
    }
  });

  failedQueue = [];
};

const leerAccessTokenSeguro = () => {
  return (
    getAccessToken?.() ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("token")
  );
};

const leerRefreshTokenSeguro = () => {
  return getRefreshToken?.() || localStorage.getItem("refresh_token");
};

const guardarAccessTokenSeguro = (token) => {
  if (!token) return;

  updateAccessToken?.(token);
  localStorage.setItem("access_token", token);
  localStorage.setItem("token", token);
};

const guardarRefreshTokenSeguro = (token) => {
  if (!token) return;

  updateRefreshToken?.(token);
  localStorage.setItem("refresh_token", token);
};

const cerrarSesionSegura = () => {
  clearSession?.();

  localStorage.removeItem("token");
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");

  window.location.href = "/";
};

// ============================================================
// REQUEST INTERCEPTOR
// ============================================================

api.interceptors.request.use(
  (config) => {
    const token = leerAccessTokenSeguro();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    config.headers["X-Client-App"] = "SGA-SaaS-Frontend";

    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================================
// RESPONSE INTERCEPTOR
// ============================================================

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (!error.response) {
      return Promise.reject(error);
    }

    const status = error.response.status;

    const url = originalRequest?.url || "";

    const isAuthEndpoint =
      url.includes("/auth/login") ||
      url.includes("/auth/refresh") ||
      url.includes("/auth/logout");

    if (status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;

      const refreshToken = leerRefreshTokenSeguro();

      if (!refreshToken) {
        cerrarSesionSegura();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;

      try {
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const newAccessToken = response.data.access_token;
        const newRefreshToken = response.data.refresh_token;

        guardarAccessTokenSeguro(newAccessToken);
        guardarRefreshTokenSeguro(newRefreshToken);

        processQueue(null, newAccessToken);

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        cerrarSesionSegura();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;