import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import API from "../../api/axios";
import MantenimientosPage from "../admin/MantenimientosPage";
import CoordinadorEquipos from "./CoordinadorEquipos";
import CoordinadorHojaVida from "./CoordinadorHojaVida";

vi.mock("../../api/axios", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const catalogos = {
  empresas: [{ id: "empresa-1", nombre: "Empresa Uno" }],
  sedes: [{ id: "sede-1", empresa_id: "empresa-1", nombre: "Sede Uno" }],
  equipos: [{
    id: "equipo-1",
    empresa_id: "empresa-1",
    sede_id: "sede-1",
    nombre: "Equipo Uno",
    ubicacion: "Consultorio 1",
  }],
  tecnicos: [{ id: "tecnico-1", nombre: "Tecnico Uno" }],
  categorias: [],
};

describe("Portal Coordinador", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("hereda el modulo profesional de mantenimiento con APIs del coordinador", async () => {
    API.get.mockImplementation(async (url) => {
      if (url === "/coordinador/mantenimientos") return { data: [] };
      if (url === "/coordinador/catalogos") return { data: catalogos };
      throw new Error(`Solicitud inesperada: ${url}`);
    });

    render(
      <MemoryRouter>
        <MantenimientosPage mode="coordinador" embedded />
      </MemoryRouter>,
    );

    expect(await screen.findByRole("heading", { name: "Mantenimientos" })).toBeInTheDocument();
    await waitFor(() => {
      expect(API.get).toHaveBeenCalledWith("/coordinador/mantenimientos");
      expect(API.get).toHaveBeenCalledWith("/coordinador/catalogos");
    });
    expect(API.get).not.toHaveBeenCalledWith("/mantenimientos/");
    expect(screen.getByDisplayValue("Empresa Uno")).toBeEnabled();
  });

  it("exporta el inventario desde el endpoint limitado del coordinador", async () => {
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL: vi.fn(() => "blob:inventario"),
      revokeObjectURL: vi.fn(),
    });
    API.get.mockImplementation(async (url) => {
      if (url === "/coordinador/equipos") return { data: [] };
      if (url === "/coordinador/catalogos") return { data: catalogos };
      if (url === "/coordinador/equipos/exportar") {
        return {
          data: new Blob(["inventario"]),
          headers: {
            "content-disposition": 'attachment; filename="inventario_coordinador.xlsx"',
          },
        };
      }
      throw new Error(`Solicitud inesperada: ${url}`);
    });

    render(
      <MemoryRouter>
        <CoordinadorEquipos />
      </MemoryRouter>,
    );

    fireEvent.click(await screen.findByRole("button", { name: "Exportar filtrado" }));

    await waitFor(() => {
      expect(API.get).toHaveBeenCalledWith(
        "/coordinador/equipos/exportar",
        {
          responseType: "blob",
          params: {
            busqueda: undefined,
            sede_id: undefined,
            categoria_id: undefined,
            estado: undefined,
            criticidad: undefined,
          },
        },
      );
      expect(click).toHaveBeenCalled();
    });
  });

  it("carga la hoja de vida PRO con historial y permite guardar", async () => {
    API.get.mockImplementation(async (url) => {
      if (url === "/coordinador/equipos") return { data: catalogos.equipos };
      if (url === "/coordinador/equipos/equipo-1/hoja-vida") {
        return {
          data: {
            encabezado: { empresa_nombre: "Empresa Uno", sede_nombre: "Sede Uno" },
            equipo_basico: {
              ...catalogos.equipos[0],
              categoria_nombre: "Biomedico",
              marca: "Marca Uno",
              modelo: "Modelo Uno",
              serie: "SER-001",
              inventario: "INV-001",
              estado: "OPERATIVO",
              criticidad: "ALTA",
            },
            hoja_vida_tecnica: { proveedor: "Proveedor inicial" },
          },
        };
      }
      if (url === "/coordinador/mantenimientos") {
        return { data: [{ id: "mant-1", tipo: "PREVENTIVO", estado: "FINALIZADO", tecnico_nombre: "Tecnico Uno" }] };
      }
      throw new Error(`Solicitud inesperada: ${url}`);
    });
    API.put.mockResolvedValue({ data: { proveedor: "Proveedor actualizado", updated_at: "2026-08-17T10:00:00" } });

    render(
      <MemoryRouter initialEntries={["/coordinador/hoja-vida/equipo-1"]}>
        <Routes>
          <Route path="/coordinador/hoja-vida/:equipoId" element={<CoordinadorHojaVida />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole("heading", { name: "Equipo Uno" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Adquisición" }));
    fireEvent.change(screen.getByLabelText("Proveedor"), { target: { value: "Proveedor actualizado" } });
    fireEvent.click(screen.getByRole("button", { name: "Guardar ahora" }));

    await waitFor(() => {
      expect(API.get).toHaveBeenCalledWith("/coordinador/mantenimientos", { params: { equipo_id: "equipo-1" } });
      expect(API.put).toHaveBeenCalledWith(
        "/coordinador/equipos/equipo-1/hoja-vida",
        expect.objectContaining({ proveedor: "Proveedor actualizado" }),
      );
    });

    fireEvent.click(screen.getByRole("button", { name: "Mantenimientos" }));
    expect(screen.getByText("PREVENTIVO")).toBeInTheDocument();
  });
});
