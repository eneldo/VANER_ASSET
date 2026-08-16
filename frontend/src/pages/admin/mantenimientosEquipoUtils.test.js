import { describe, expect, it } from "vitest";
import {
  UBICACION_SIN_REGISTRO,
  construirEtiquetaEquipo,
  encontrarUbicacionDisponible,
  filtrarEquiposPorUbicacion,
  listarUbicacionesEquipos,
} from "./mantenimientosEquipoUtils";

const equipos = [
  {
    id: "equipo-1",
    sede_id: "sede-1",
    nombre: "Mini Split",
    ubicacion: "Consultorio médico 15",
    inventario: "INV-015",
    codigo_id: "AA-015",
    serie: "SER-015",
  },
  {
    id: "equipo-2",
    sede_id: "sede-1",
    nombre: "Mini Split",
    ubicacion: "Consultorio médico 16",
    codigo_id: "AA-016",
  },
  {
    id: "equipo-3",
    sede_id: "sede-1",
    nombre: "Nevera",
    ubicacion: "",
  },
];

describe("mantenimientosEquipoUtils", () => {
  it("construye una etiqueta que identifica ubicación e inventario", () => {
    expect(construirEtiquetaEquipo(equipos[0])).toBe(
      "Mini Split · Ubicación: Consultorio médico 15 · Inv: INV-015 · Código: AA-015 · Serie: SER-015"
    );
  });

  it("lista ubicaciones e incluye equipos sin ubicación registrada", () => {
    expect(listarUbicacionesEquipos(equipos, "sede-1")).toEqual([
      { value: "Consultorio médico 15", label: "Consultorio médico 15" },
      { value: "Consultorio médico 16", label: "Consultorio médico 16" },
      { value: UBICACION_SIN_REGISTRO, label: "Sin ubicación registrada" },
    ]);
  });

  it("filtra el activo exacto por sede y ubicación", () => {
    expect(filtrarEquiposPorUbicacion(equipos, "sede-1", "Consultorio médico 15")).toEqual([
      equipos[0],
    ]);
  });

  it("encuentra la ubicación escrita sin respetar mayúsculas ni acentos", () => {
    const ubicaciones = listarUbicacionesEquipos(equipos, "sede-1");

    expect(encontrarUbicacionDisponible(ubicaciones, "consultorio medico 15")).toEqual({
      value: "Consultorio médico 15",
      label: "Consultorio médico 15",
    });
    expect(encontrarUbicacionDisponible(ubicaciones, "sin ubicacion registrada")).toEqual({
      value: UBICACION_SIN_REGISTRO,
      label: "Sin ubicación registrada",
    });
  });
});
