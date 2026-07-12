import { describe, expect, it } from "vitest";
import { isNetworkError } from "./offlineQueue";

describe("detección de conectividad offline", () => {
  it("clasifica errores sin respuesta como errores de red", () => {
    expect(isNetworkError(new Error("Network Error"))).toBe(true);
  });

  it("no encola errores HTTP cuando existe conexión", () => {
    Object.defineProperty(navigator, "onLine", { configurable: true, value: true });
    expect(isNetworkError({ response: { status: 422 } })).toBe(false);
  });
});
