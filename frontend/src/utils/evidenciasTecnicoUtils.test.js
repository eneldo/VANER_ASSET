import { describe, expect, it } from "vitest";
import {
  contarEvidenciasPorTipo,
  obtenerCuposEvidencia,
  validarSeleccionEvidencias,
} from "./evidenciasTecnicoUtils";

describe("evidenciasTecnicoUtils", () => {
  const evidencias = [
    { tipo: "ANTES" },
    { tipo: "antes" },
    { tipo: "DURANTE" },
  ];

  it("cuenta evidencias sin depender de mayúsculas", () => {
    expect(contarEvidenciasPorTipo(evidencias, "ANTES")).toBe(2);
    expect(obtenerCuposEvidencia(evidencias, "ANTES")).toBe(2);
  });

  it("permite seleccionar solo los cupos disponibles", () => {
    const archivos = [{ name: "uno.jpg" }, { name: "dos.jpg" }];
    const resultado = validarSeleccionEvidencias(archivos, evidencias, "ANTES");

    expect(resultado.error).toBe("");
    expect(resultado.archivos).toHaveLength(2);
  });

  it("rechaza una selección que supere cuatro por etapa", () => {
    const resultado = validarSeleccionEvidencias(
      [{ name: "uno.jpg" }],
      Array.from({ length: 4 }, () => ({ tipo: "DESPUES" })),
      "DESPUES"
    );

    expect(resultado.archivos).toHaveLength(0);
    expect(resultado.error).toContain("máximo de 4 evidencias");
  });

  it("mantiene soporte fuera del límite de etapas", () => {
    expect(obtenerCuposEvidencia(evidencias, "SOPORTE")).toBeNull();
  });
});
