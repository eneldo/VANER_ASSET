import { describe, expect, it, vi } from "vitest";
import { getEmpresaId, getUserRole, isAdminLike, isClienteLike } from "./multiempresa";

describe("contexto multiempresa del cliente", () => {
  it("prioriza el tenant firmado en el usuario", () => {
    localStorage.setItem("empresa_id", "empresa-incorrecta");
    localStorage.setItem("user", JSON.stringify({ rol: "empresa", empresa_id: "empresa-correcta" }));
    expect(getEmpresaId()).toBe("empresa-correcta");
    expect(getUserRole()).toBe("EMPRESA");
    expect(isClienteLike()).toBe(true);
    expect(isAdminLike()).toBe(false);
  });

  it("normaliza roles administrativos", () => {
    localStorage.setItem("user", JSON.stringify({ role: "coordinador" }));
    expect(getUserRole()).toBe("COORDINADOR");
    expect(isAdminLike()).toBe(true);
  });

  it("no deriva un tenant desde un usuario corrupto", () => {
    localStorage.setItem("user", "invalido");
    vi.spyOn(console, "error").mockImplementation(() => {});
    expect(getEmpresaId()).toBeNull();
    expect(getUserRole()).toBe("");
  });
});
