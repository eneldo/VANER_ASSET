// ============================================================
// API: Configuración Inteligente SaaS
// Archivo: frontend/src/api/configuracionApi.js
// Fase 34.1 - Configuración Inteligente SaaS PRO
// ============================================================

import api from "./axios";

export const configuracionApi = {
  obtener: async () => {
    const { data } = await api.get("/configuracion-saas/");
    return data;
  },

  guardar: async (payload) => {
    const { data } = await api.put("/configuracion-saas/", payload);
    return data;
  },

  subirLogo: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await api.post("/configuracion-saas/logo", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  probarCorreo: async (payload) => {
    const { data } = await api.post("/configuracion-saas/test-email", payload);
    return data;
  },

  probarBackup: async () => {
    const { data } = await api.post("/configuracion-saas/backup/probar");
    return data;
  },
};
