// ============================================================
// AUTH STORAGE PRO
// Archivo: frontend/src/utils/authStorage.js
// ============================================================
// Centraliza el manejo de tokens y usuario.
// Esto evita tener localStorage disperso por todo el frontend.
// ============================================================

const USER_KEY = "user";
const SESSION_CREATED_AT_KEY = "session_created_at";
let accessToken = null;

export function saveSession({ access_token, user }) {
  if (access_token) accessToken = access_token;
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));

  localStorage.removeItem("access_token");
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.setItem(SESSION_CREATED_AT_KEY, new Date().toISOString());
}

export function getAccessToken() {
  return accessToken;
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    console.error("Error leyendo usuario almacenado:", error);
    return null;
  }
}

export function updateAccessToken(token) {
  if (token) {
    accessToken = token;
  }
}

export function clearSession() {
  accessToken = null;
  localStorage.removeItem("access_token");
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(SESSION_CREATED_AT_KEY);
  localStorage.removeItem("coordinator_active_company_id");
}

export function isSessionActive() {
  return Boolean(getAccessToken() && getStoredUser());
}
