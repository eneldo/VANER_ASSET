import { describe, expect, it, vi } from "vitest";
import { clearSession, getAccessToken, getRefreshToken, getStoredUser, isSessionActive, saveSession } from "./authStorage";

describe("almacenamiento seguro de sesión", () => {
  it("guarda y recupera una sesión completa", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-07-12T12:00:00Z"));
    saveSession({ access_token: "access", refresh_token: "refresh", user: { id: "u1", rol: "EMPRESA", empresa_id: "empresa-a" } });
    expect(getAccessToken()).toBe("access");
    expect(getRefreshToken()).toBe("refresh");
    expect(getStoredUser()).toMatchObject({ rol: "EMPRESA", empresa_id: "empresa-a" });
    expect(isSessionActive()).toBe(true);
    expect(localStorage.getItem("session_created_at")).toBe("2026-07-12T12:00:00.000Z");
    vi.useRealTimers();
  });

  it("elimina todos los datos de autenticación", () => {
    saveSession({ access_token: "a", refresh_token: "r", user: { id: "u1" } });
    clearSession();
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
    expect(getStoredUser()).toBeNull();
    expect(isSessionActive()).toBe(false);
  });

  it("rechaza silenciosamente un usuario local corrupto", () => {
    localStorage.setItem("user", "{json-invalido");
    vi.spyOn(console, "error").mockImplementation(() => {});
    expect(getStoredUser()).toBeNull();
    expect(isSessionActive()).toBe(false);
  });
});
