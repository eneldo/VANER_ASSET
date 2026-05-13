// ============================================================
// AUTH STORAGE PRO
// Archivo: frontend/src/utils/authStorage.js
// ============================================================
// Centraliza el manejo de tokens y usuario.
// Esto evita tener localStorage disperso por todo el frontend.
// ============================================================

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "user";
const SESSION_CREATED_AT_KEY = "session_created_at";

export function saveSession({ access_token, refresh_token, user }) {
  if (access_token) localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));

  localStorage.setItem(SESSION_CREATED_AT_KEY, new Date().toISOString());
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
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
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
  }
}

export function updateRefreshToken(token) {
  if (token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }
}

export function clearSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(SESSION_CREATED_AT_KEY);
}

export function isSessionActive() {
  return Boolean(getAccessToken() && getStoredUser());
}
