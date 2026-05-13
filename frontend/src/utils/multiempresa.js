/*
FASE 31.6 - MULTIEMPRESA SEGURA PRO
Archivo: frontend/src/utils/multiempresa.js

Objetivo:
- Obtener usuario autenticado desde localStorage.
- Centralizar empresa_id y rol en frontend.
- Recordatorio: la seguridad real se hace en backend.
*/

export function getStoredUser() {
  try {
    const raw = localStorage.getItem("user") || localStorage.getItem("usuario");
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    console.error("Error leyendo usuario local:", error);
    return null;
  }
}

export function getUserRole() {
  const user = getStoredUser();
  return String(user?.rol || user?.role || "").toUpperCase();
}

export function getEmpresaId() {
  const user = getStoredUser();
  return user?.empresa_id || localStorage.getItem("empresa_id") || null;
}

export function isAdminLike() {
  const rol = getUserRole();
  return rol === "ADMIN" || rol === "COORDINADOR";
}

export function isClienteLike() {
  const rol = getUserRole();
  return rol === "CLIENTE" || rol === "EMPRESA";
}
