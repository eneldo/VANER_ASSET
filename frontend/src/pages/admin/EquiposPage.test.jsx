import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { AuthContext } from "../../context/auth-context";
import EquiposPage from "./EquiposPage";


function jsonResponse(data) {
  return {
    ok: true,
    json: async () => data,
  };
}


describe("EquiposPage", () => {
  it("precarga y actualiza la hoja de vida al editar un equipo", async () => {
    const equipo = {
      id: "equipo-1",
      empresa_id: "empresa-1",
      sede_id: "sede-1",
      categoria_id: "categoria-1",
      nombre: "Aire acondicionado",
      marca: "Marca",
      modelo: "Modelo",
      serie: "Serie",
      ubicacion: "Consultorio",
      codigo_id: "EQ-001",
      inventario: "INV-001",
      estado: "OPERATIVO",
      criticidad: "MEDIA",
      activo: true,
    };
    const hoja = {
      id: "hoja-1",
      equipo_id: equipo.id,
      adquisicion: "Compra directa",
      costo: "1500000.00",
      fecha_compra: "2026-01-10",
      fecha_instalacion: "2026-01-15",
      proveedor: "Proveedor local",
      pais_fabricacion: "Colombia",
      fecha_fabricacion: "2025-12-01",
      vida_util: "10 anos",
      rango_voltaje: "220V",
      gas_refrigerante: "R410",
      capacidad: "18BTU",
      rango_potencia: "1550W",
      requiere_calibracion: true,
      manual_operacion: true,
    };

    vi.stubGlobal("fetch", vi.fn(async (input, options = {}) => {
      const url = String(input);

      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) {
        return jsonResponse([{ id: "sede-1", empresa_id: "empresa-1", nombre: "Sede" }]);
      }
      if (url.endsWith("/categorias/")) {
        return jsonResponse([{ id: "categoria-1", nombre: "Aires" }]);
      }
      if (url.endsWith("/equipos/")) {
        return jsonResponse([equipo]);
      }
      if (url.endsWith("/equipo-hoja-vida/equipo/equipo-1") && options.method === "PUT") {
        return jsonResponse({ ...hoja, ...JSON.parse(options.body) });
      }
      if (url.endsWith("/equipo-hoja-vida/equipo/equipo-1")) {
        return { ...jsonResponse(hoja), status: 200 };
      }

      throw new Error(`Solicitud inesperada: ${url}`);
    }));

    render(
      <AuthContext.Provider
        value={{
          user: { rol: "ADMIN", nombre_completo: "Admin SGA" },
          logout: vi.fn(),
        }}
      >
        <MemoryRouter initialEntries={["/admin/equipos"]}>
          <EquiposPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    fireEvent.click(await screen.findByTitle("Editar"));
    const pasoHoja = await screen.findByRole("button", { name: "2. Hoja de vida" });

    await waitFor(() => expect(pasoHoja).toBeEnabled());
    expect(screen.getByLabelText("Inventario")).toHaveValue("INV-001");
    expect(screen.queryByText(/Equipo ya existe: el número de inventario/)).not.toBeInTheDocument();
    fireEvent.click(pasoHoja);

    expect(await screen.findByDisplayValue("Compra directa")).toBeInTheDocument();
    expect(screen.getByDisplayValue("220V")).toBeInTheDocument();
    expect(screen.getByDisplayValue("R410")).toBeInTheDocument();
    expect(screen.getByDisplayValue("18BTU")).toBeInTheDocument();
    expect(screen.getByDisplayValue("1550W")).toBeInTheDocument();
    expect(screen.getByLabelText("Requiere calibración")).toBeChecked();
    expect(screen.getByLabelText("Manual operación")).toBeChecked();

    fireEvent.change(screen.getByDisplayValue("18BTU"), {
      target: { name: "capacidad", value: "24BTU" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Finalizar hoja de vida" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        "/api/equipo-hoja-vida/equipo/equipo-1",
        expect.objectContaining({
          method: "PUT",
          body: expect.any(String),
        }),
      );
    });

    const llamadaPut = fetch.mock.calls.find(
      ([url, options]) => String(url).endsWith("/equipo-hoja-vida/equipo/equipo-1")
        && options?.method === "PUT",
    );
    const payload = JSON.parse(llamadaPut[1].body);

    expect(payload.capacidad).toBe("24BTU");
    expect(payload).not.toHaveProperty("equipo_id");
  });

  it("avisa y bloquea el guardado cuando el inventario ya existe", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input) => {
      const url = String(input);

      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) {
        return jsonResponse([{ id: "sede-1", empresa_id: "empresa-1", nombre: "Sede" }]);
      }
      if (url.endsWith("/categorias/")) {
        return jsonResponse([{ id: "categoria-1", nombre: "Aires" }]);
      }
      if (url.endsWith("/equipos/")) {
        return jsonResponse([{
          id: "equipo-existente",
          empresa_id: "empresa-1",
          sede_id: "sede-1",
          categoria_id: "categoria-1",
          nombre: "Equipo existente",
          inventario: "INV-001",
          estado: "OPERATIVO",
          criticidad: "MEDIA",
          activo: true,
        }]);
      }

      throw new Error(`Solicitud inesperada: ${url}`);
    }));

    render(
      <AuthContext.Provider
        value={{
          user: { rol: "ADMIN", nombre_completo: "Admin SGA" },
          logout: vi.fn(),
        }}
      >
        <MemoryRouter initialEntries={["/admin/equipos"]}>
          <EquiposPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    fireEvent.click(await screen.findByRole("button", { name: "Nuevo Equipo" }));
    fireEvent.change(screen.getByLabelText("Inventario"), {
      target: { name: "inventario", value: "  inv-001  " },
    });

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Equipo ya existe: el número de inventario está registrado.",
    );
    expect(screen.getByRole("button", { name: "Guardar y continuar" })).toBeDisabled();
  });

  it("exporta el inventario desde la cabecera", async () => {
    const createObjectURL = vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:inventario");
    const revokeObjectURL = vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {});
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    vi.stubGlobal("fetch", vi.fn(async (input) => {
      const url = String(input);
      if (url.endsWith("/equipos/exportar")) {
        return {
          ok: true,
          headers: new Headers({
            "content-disposition": 'attachment; filename="inventario_equipos_sga.xlsx"',
          }),
          blob: async () => new Blob(["excel"]),
        };
      }
      return jsonResponse([]);
    }));

    render(
      <AuthContext.Provider
        value={{
          user: { rol: "ADMIN", nombre_completo: "Admin SGA" },
          logout: vi.fn(),
        }}
      >
        <MemoryRouter initialEntries={["/admin/equipos"]}>
          <EquiposPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    fireEvent.click(await screen.findByRole("button", { name: "Exportar Excel" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        "/api/equipos/exportar",
        expect.objectContaining({ headers: expect.any(Object) }),
      );
      expect(screen.getByText("Inventario exportado correctamente.")).toBeInTheDocument();
    });

    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:inventario");
  });
});
