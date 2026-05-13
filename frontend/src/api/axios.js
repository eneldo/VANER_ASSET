// ============================================================
// AXIOS PRO CON REFRESH TOKEN AUTOMÁTICO
// Archivo: frontend/src/api/axios.js
// ============================================================
// Maneja:
// - Base URL centralizada.
// - Authorization Bearer automático.
// - Renovación automática con refresh_token.
// - Logout seguro si el refresh falla.
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

// Controla múltiples errores 401 simultáneos.
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

// ============================================================
// REQUEST INTERCEPTOR
// Agrega el access token automáticamente.
// ============================================================

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

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
// Si recibe 401, intenta renovar sesión usando refresh_token.
// ============================================================

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (!error.response) {
      return Promise.reject(error);
    }

    const status = error.response.status;

    // Evita bucles infinitos con login/refresh/logout.
    const isAuthEndpoint =
      originalRequest?.url?.includes("/auth/login") ||
      originalRequest?.url?.includes("/auth/refresh") ||
      originalRequest?.url?.includes("/auth/logout");

    if (status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;

      const refreshToken = getRefreshToken();

      if (!refreshToken) {
        clearSession();
        window.location.href = "/login";
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

        updateAccessToken(newAccessToken);

        if (newRefreshToken) {
          updateRefreshToken(newRefreshToken);
        }

        processQueue(null, newAccessToken);

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearSession();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
