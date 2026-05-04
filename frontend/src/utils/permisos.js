// ============================================================
// HELPER: Permisos Frontend
// Archivo: frontend/src/utils/permisos.js
// ============================================================

export function getPermisos() {
  try {
    return JSON.parse(localStorage.getItem("permisos") || "[]");
  } catch {
    return [];
  }
}

export function tienePermiso(codigo) {
  const permisos = getPermisos();

  return permisos.includes(codigo);
}

export function tieneAlguno(codigos = []) {
  const permisos = getPermisos();

  return codigos.some((codigo) => permisos.includes(codigo));
}

export function esAdmin() {
  const rol = localStorage.getItem("rol") || "";

  return rol.toUpperCase() === "ADMIN";
}