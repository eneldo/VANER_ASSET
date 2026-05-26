// ============================================================
// API: SMTP Inteligente SaaS PRO
// Archivo: frontend/src/api/smtpInteligenteApi.js
// FASE 34.2.3
// ============================================================

import api from "./axios";

const BASE = "/smtp-inteligente";

export const inicializarSMTP = async () => {
  const { data } = await api.post(`${BASE}/inicializar`);
  return data;
};

export const obtenerEstadoSMTP = async () => {
  const { data } = await api.get(`${BASE}/estado`);
  return data;
};

export const obtenerPlantillasSMTP = async () => {
  const { data } = await api.get(`${BASE}/plantillas`);
  return data;
};

export const probarSMTP = async (payload) => {
  const { data } = await api.post(`${BASE}/probar`, payload);
  return data;
};

export const enviarCorreoManual = async (payload) => {
  const { data } = await api.post(`${BASE}/enviar`, payload);
  return data;
};

export const listarLogsSMTP = async (limit = 50) => {
  const { data } = await api.get(`${BASE}/logs`, { params: { limit } });
  return data;
};
