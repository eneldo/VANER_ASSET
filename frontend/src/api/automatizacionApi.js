// ============================================================
// API: Automatización SaaS PRO
// Archivo: frontend/src/api/automatizacionApi.js
// ============================================================

import api from "./axios";

export const automatizacionApi = {
  inicializar: async () => {
    const { data } = await api.post("/automatizacion/inicializar");
    return data;
  },

  listar: async () => {
    const { data } = await api.get("/automatizacion/");
    return data;
  },

  actualizar: async (modulo, payload) => {
    const { data } = await api.put(`/automatizacion/${modulo}`, payload);
    return data;
  },

  toggle: async (modulo) => {
    const { data } = await api.post(`/automatizacion/${modulo}/toggle`);
    return data;
  },

  schedulerStatus: async () => {
    const { data } = await api.get("/automatizacion/scheduler/status");
    return data;
  },

  reiniciarScheduler: async () => {
    const { data } = await api.post("/automatizacion/scheduler/reiniciar");
    return data;
  },

  monitor: async () => {
    const { data } = await api.get("/automatizacion/monitor");
    return data;
  },

  logs: async (limite = 100) => {
    const { data } = await api.get(`/automatizacion/logs?limite=${limite}`);
    return data;
  },
};

export default automatizacionApi;
