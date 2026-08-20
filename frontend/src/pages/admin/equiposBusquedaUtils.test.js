import { describe, expect, it } from "vitest";
import {
  coincideBusquedaEquipo,
  coincideBusquedaEquipoConContexto,
  normalizarTextoBusqueda,
} from "./equiposBusquedaUtils";

describe("equiposBusquedaUtils", () => {
  it("ignora tildes y mayúsculas", () => {
    expect(normalizarTextoBusqueda("CÁMARA de Seguridad")).toBe("camara de seguridad");
    expect(coincideBusquedaEquipo(["Cámaras de seguridad"], "camara")).toBe(true);
  });

  it("encuentra equipos usando singular o plural", () => {
    expect(coincideBusquedaEquipo(["Cámara de seguridad"], "camaras")).toBe(true);
    expect(coincideBusquedaEquipo(["Ascensores"], "ascensor")).toBe(true);
    expect(coincideBusquedaEquipo(["Aire acondicionado"], "aires")).toBe(true);
  });

  it("ignora conectores y permite búsquedas por varias palabras", () => {
    expect(coincideBusquedaEquipo(["Cámaras seguridad IP"], "camara de seguridad")).toBe(true);
    expect(coincideBusquedaEquipo(["Cámara térmica"], "camara seguridad")).toBe(false);
  });

  it("permite buscar mientras el usuario termina de escribir", () => {
    expect(coincideBusquedaEquipo(["Refrigeradores industriales"], "refrig indus")).toBe(true);
  });

  it("usa la categoría solo como contexto y no incluye accesorios", () => {
    const categoria = ["Cámaras de seguridad"];
    const equipos = ["Cámara IP Hikvision", "Monitor 24 pulgadas", "Disco duro 4 TB"];
    const resultados = equipos.filter((equipo) =>
      coincideBusquedaEquipoConContexto([equipo], categoria, "camara de seguridad")
    );

    expect(resultados).toEqual(["Cámara IP Hikvision"]);
    expect(resultados).toHaveLength(1);
  });

  it.each(["cámara", "camara", "camaras", "CÁMARA"])(
    "reconoce la variante %s sin incluir accesorios",
    (busqueda) => {
      const categoria = ["Cámaras de seguridad"];
      const equipos = ["Cámara IP Hikvision", "Monitor 24 pulgadas", "Disco duro 4 TB"];
      const resultados = equipos.filter((equipo) =>
        coincideBusquedaEquipoConContexto([equipo], categoria, busqueda)
      );

      expect(resultados).toEqual(["Cámara IP Hikvision"]);
    }
  );
});
