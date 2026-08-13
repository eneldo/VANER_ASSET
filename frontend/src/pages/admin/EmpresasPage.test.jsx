import { describe, expect, it } from "vitest";
import { construirPayloadEmpresa, obtenerMensajeError } from "./empresaFormUtils";

describe("EmpresasPage", () => {
  it("envia como null los campos opcionales vacios", () => {
    expect(construirPayloadEmpresa({
      nombre: "  Empresa local  ",
      nit: " ",
      telefono: "",
      direccion: "  ",
      correo: "",
      logo_url: " ",
      activo: true,
    })).toEqual({
      nombre: "Empresa local",
      nit: null,
      telefono: null,
      direccion: null,
      correo: null,
      logo_url: null,
      activo: true,
    });
  });

  it("convierte los errores de validacion del backend en texto legible", () => {
    const error = {
      response: {
        data: {
          detail: [
            {
              loc: ["body", "correo"],
              msg: "value is not a valid email address",
            },
          ],
        },
      },
    };

    expect(obtenerMensajeError(error, "Error guardando empresa")).toBe(
      "Correo corporativo: value is not a valid email address",
    );
  });

  it("conserva los mensajes simples enviados por el backend", () => {
    const error = { response: { data: { detail: "Empresa no encontrada" } } };

    expect(obtenerMensajeError(error, "Error guardando empresa")).toBe(
      "Empresa no encontrada",
    );
  });
});
