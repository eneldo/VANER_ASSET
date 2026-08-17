import { describe, expect, it } from "vitest";
import { isImageEvidence, isPdfEvidence } from "./evidenciaUtils";

describe("evidenciaUtils", () => {
  it("detecta imágenes por el nombre original", () => {
    expect(isImageEvidence({ nombre_original: "foto equipo.JPG" })).toBe(true);
  });

  it("detecta imágenes dentro de una URL firmada", () => {
    expect(isImageEvidence({ archivo_url: "/evidencias/1/archivo?filename=foto.webp" })).toBe(true);
  });

  it("detecta archivos PDF", () => {
    expect(isPdfEvidence({ content_type: "application/pdf" })).toBe(true);
  });
});
