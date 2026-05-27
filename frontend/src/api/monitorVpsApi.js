// ============================================================
// API MONITOR VPS + POSTGRESQL PRO
// Archivo: frontend/src/api/monitorVpsApi.js
// Fase 34.2.4
// ============================================================

import api from "./axios";

export const monitorVpsApi = {
  async resumen() {
    const { data } = await api.get("/monitor-vps/resumen");
    return data;
  },

  async vps() {
    const { data } = await api.get("/monitor-vps/vps");
    return data;
  },

  async postgresql() {
    const { data } = await api.get("/monitor-vps/postgresql");
    return data;
  },

  async docker() {
    const { data } = await api.get("/monitor-vps/docker");
    return data;
  },

  async health() {
    const { data } = await api.get("/monitor-vps/health");
    return data;
  },
};
