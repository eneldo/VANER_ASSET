// ============================================================
// API: Configuración Inteligente SaaS
// Archivo: frontend/src/api/configuracionApi.js
// Fase 34.1 - Configuración Inteligente SaaS PRO
//
// Correcciones aplicadas:
// - Centraliza endpoint /configuracion-saas.
// - Mantiene compatibilidad con axios.js y VITE_API_URL.
// - Devuelve errores claros al frontend.
// ============================================================

import api from "./axios";

const BASE = "/configuracion-saas";

function normalizeError(error) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;
  const message =
    typeof detail === "string"
      ? detail
      : error?.message || "Error desconocido al conectar con el backend.";

  return {
    status,
    message,
    raw: error,
  };
}

export const configuracionApi = {
  obtener: async () => {
    try {
      const { data } = await api.get(`${BASE}/`);
      return data;
    } catch (error) {
      throw normalizeError(error);
    }
  },

  guardar: async (payload) => {
    try {
      const { data } = await api.put(`${BASE}/`, payload);
      return data;
    } catch (error) {
      throw normalizeError(error);
    }
  },

  subirLogo: async (file) => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const { data } = await api.post(`${BASE}/logo`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      return data;
    } catch (error) {
      throw normalizeError(error);
    }
  },

  probarCorreo: async (payload) => {
    try {
      const { data } = await api.post(`${BASE}/test-email`, payload);
      return data;
    } catch (error) {
      throw normalizeError(error);
    }
  },

  probarBackup: async () => {
    try {
      const { data } = await api.post(`${BASE}/backup/probar`);
      return data;
    } catch (error) {
      throw normalizeError(error);
    }
  },
};
