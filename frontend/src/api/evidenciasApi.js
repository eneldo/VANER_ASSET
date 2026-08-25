/*
===========================================================
API SEGURA EVIDENCIAS
Archivo: frontend/src/api/evidenciasApi.js

FIX PRODUCCIÓN:
- No usar 127.0.0.1.
- Usa VITE_API_URL.
===========================================================
*/

import axios from "axios";
import { getAccessToken } from "../utils/authStorage";

const API_BASE =
  import.meta.env.VITE_API_URL ||
  window.location.origin;

const API = `${String(API_BASE).replace(/\/$/, "")}/evidencias`;

function getToken() {
  return getAccessToken();
}

export const subirEvidencia = async (formData) => {
  const token = getToken();

  return axios.post(`${API}/subir`, formData, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "Content-Type": "multipart/form-data",
    },
  });
};

export const listarEvidencias = async () => {
  const token = getToken();

  return axios.get(`${API}/`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
};

export const listarEvidenciasPorEquipo = async (equipoId) => {
  const token = getToken();

  return axios.get(`${API}/equipo/${equipoId}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
};

export const listarEvidenciasPorMantenimiento = async (mantenimientoId) => {
  const token = getToken();

  return axios.get(`${API}/mantenimiento/${mantenimientoId}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
};
