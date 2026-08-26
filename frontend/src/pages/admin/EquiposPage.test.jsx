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
      if (url.endsWith("/usuarios/")) return jsonResponse([]);

      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) {
        return jsonResponse([{ id: "sede-1", empresa_id: "empresa-1", nombre: "Sede" }]);
      }
      if (url.endsWith("/categorias/")) {
        return jsonResponse([{ id: "categoria-1", nombre: "Aires" }]);
      }
      if (url.includes("/equipos/")) {
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
      if (url.endsWith("/usuarios/")) return jsonResponse([]);

      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) {
        return jsonResponse([{ id: "sede-1", empresa_id: "empresa-1", nombre: "Sede" }]);
      }
      if (url.endsWith("/categorias/")) {
        return jsonResponse([{ id: "categoria-1", nombre: "Aires" }]);
      }
      if (url.includes("/equipos/")) {
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

  it("detecta desde el formulario un inventario creado por importación", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input) => {
      const url = String(input);
      if (url.endsWith("/usuarios/")) return jsonResponse([]);

      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) {
        return jsonResponse([{ id: "sede-1", empresa_id: "empresa-1", nombre: "Sede" }]);
      }
      if (url.endsWith("/categorias/")) {
        return jsonResponse([{ id: "categoria-1", nombre: "Aires" }]);
      }
      if (url.includes("/equipos/")) {
        return jsonResponse([{
          id: "equipo-importado",
          empresa_id: "empresa-1",
          sede_id: "sede-1",
          categoria_id: "categoria-1",
          nombre: "Equipo importado",
          codigo_id: "17774",
          inventario: null,
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
      target: { name: "inventario", value: "17774" },
    });

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Equipo ya existe: el número de inventario está registrado.",
    );
    expect(screen.getByRole("button", { name: "Guardar y continuar" })).toBeDisabled();
  });

  it("busca y filtra equipos por sede desde la barra y la cabecera", async () => {
    const sedes = [
      { id: "sede-norte", empresa_id: "empresa-1", nombre: "CARI - HIPOTERAPIA" },
      { id: "sede-sur", empresa_id: "empresa-1", nombre: "Hospital Central" },
    ];
    const equipos = [
      {
        id: "equipo-norte",
        empresa_id: "empresa-1",
        sede_id: "sede-norte",
        categoria_id: "categoria-1",
        nombre: "Mini Split Norte",
        inventario: "15209",
        estado: "OPERATIVO",
        criticidad: "BAJA",
        activo: true,
      },
      {
        id: "equipo-sur",
        empresa_id: "empresa-1",
        sede_id: "sede-sur",
        categoria_id: "categoria-1",
        nombre: "Mini Split Central",
        inventario: "12147",
        estado: "OPERATIVO",
        criticidad: "BAJA",
        activo: true,
      },
    ];

    vi.stubGlobal("fetch", vi.fn(async (input) => {
      const url = String(input);
      if (url.endsWith("/usuarios/")) return jsonResponse([]);
      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) return jsonResponse(sedes);
      if (url.endsWith("/categorias/")) {
        return jsonResponse([{ id: "categoria-1", nombre: "Aires" }]);
      }
      if (url.includes("/equipos/")) return jsonResponse(equipos);

      throw new Error("Solicitud inesperada: " + url);
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

    const buscador = await screen.findByPlaceholderText(
      "Buscar equipos, cámaras, inventario o sede...",
    );
    expect(await screen.findByText("Mini Split Norte")).toBeInTheDocument();
    expect(await screen.findByText("Mini Split Central")).toBeInTheDocument();
    expect(screen.getByText("2", { selector: ".enterprise-results-summary strong" })).toBeInTheDocument();

    const equiposPorPagina = screen.getByLabelText("Equipos por página");
    expect(equiposPorPagina).toHaveValue("20");
    expect(Array.from(equiposPorPagina.options).map((option) => option.value)).toEqual(["20", "50", "100"]);
    fireEvent.change(equiposPorPagina, { target: { value: "50" } });
    expect(equiposPorPagina).toHaveValue("50");

    fireEvent.change(buscador, { target: { value: "hipoterapia" } });
    expect(screen.getByText("Mini Split Norte")).toBeInTheDocument();
    expect(screen.queryByText("Mini Split Central")).not.toBeInTheDocument();
    expect(screen.getByText("1", { selector: ".enterprise-results-summary strong" })).toBeInTheDocument();
    expect(screen.getByText("para “hipoterapia”")).toBeInTheDocument();

    fireEvent.change(buscador, { target: { value: "" } });
    fireEvent.change(screen.getByLabelText("Filtrar por sede"), {
      target: { value: "sede-sur" },
    });
    expect(screen.queryByText("Mini Split Norte")).not.toBeInTheDocument();
    expect(screen.getByText("Mini Split Central")).toBeInTheDocument();
    expect(screen.getByText("1", { selector: ".enterprise-results-summary strong" })).toBeInTheDocument();
    expect(screen.getByText("en Hospital Central")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Abrir filtro de sedes" }));
    expect(screen.getByRole("menu", { name: "Sedes disponibles" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("menuitem", { name: "CARI - HIPOTERAPIA" }));

    expect(screen.getByLabelText("Filtrar por sede")).toHaveValue("sede-norte");
    expect(screen.getByText("Mini Split Norte")).toBeInTheDocument();
    expect(screen.queryByText("Mini Split Central")).not.toBeInTheDocument();
  });

  it("filtra cámaras reales sin incluir accesorios de la misma categoría", async () => {
    const sede = { id: "sede-1", empresa_id: "empresa-1", nombre: "Sede Principal" };
    const categoria = { id: "categoria-camaras", nombre: "Cámaras de seguridad" };
    const equipos = [
      {
        id: "camara-1",
        empresa_id: "empresa-1",
        sede_id: sede.id,
        categoria_id: categoria.id,
        nombre: "Cámara IP Hikvision",
        estado: "OPERATIVO",
        criticidad: "MEDIA",
        activo: true,
      },
      {
        id: "monitor-1",
        empresa_id: "empresa-1",
        sede_id: sede.id,
        categoria_id: categoria.id,
        nombre: "Monitor 24 pulgadas",
        estado: "OPERATIVO",
        criticidad: "BAJA",
        activo: true,
      },
      {
        id: "disco-1",
        empresa_id: "empresa-1",
        sede_id: sede.id,
        categoria_id: categoria.id,
        nombre: "Disco duro 4 TB",
        estado: "OPERATIVO",
        criticidad: "BAJA",
        activo: true,
      },
    ];

    vi.stubGlobal("fetch", vi.fn(async (input) => {
      const url = String(input);
      if (url.endsWith("/usuarios/")) return jsonResponse([]);
      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) return jsonResponse([sede]);
      if (url.endsWith("/categorias/")) return jsonResponse([categoria]);
      if (url.includes("/equipos/")) return jsonResponse(equipos);

      throw new Error("Solicitud inesperada: " + url);
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

    const buscador = await screen.findByPlaceholderText(
      "Buscar equipos, cámaras, inventario o sede...",
    );

    for (const busqueda of ["camara de seguridad", "cámara", "camara", "camaras", "CÁMARA"]) {
      fireEvent.change(buscador, { target: { value: busqueda } });
      expect(screen.getByText("Cámara IP Hikvision")).toBeInTheDocument();
      expect(screen.queryByText("Monitor 24 pulgadas")).not.toBeInTheDocument();
      expect(screen.queryByText("Disco duro 4 TB")).not.toBeInTheDocument();
      expect(screen.getByText("1", { selector: ".enterprise-results-summary strong" })).toBeInTheDocument();
    }
  });

  it("permite importar nuevamente y muestra las filas omitidas", async () => {
    const sedes = [
      { id: "sede-1", empresa_id: "empresa-1", nombre: "Sede Uno" },
      { id: "sede-2", empresa_id: "empresa-1", nombre: "Sede Dos" },
    ];
    const equiposIniciales = [{
      id: "equipo-1",
      empresa_id: "empresa-1",
      sede_id: "sede-1",
      categoria_id: "categoria-1",
      nombre: "Equipo existente",
      inventario: "INV-001",
      estado: "OPERATIVO",
      criticidad: "BAJA",
      activo: true,
    }];
    const equipoNuevo = {
      ...equiposIniciales[0],
      id: "equipo-2",
      sede_id: "sede-2",
      nombre: "Equipo nuevo",
      inventario: "INV-002",
    };
    let importado = false;

    vi.stubGlobal("fetch", vi.fn(async (input, options = {}) => {
      const url = String(input);
      if (url.endsWith("/usuarios/")) return jsonResponse([]);
      if (url.endsWith("/empresas/")) {
        return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      }
      if (url.endsWith("/sedes/")) return jsonResponse(sedes);
      if (url.endsWith("/categorias/")) {
        return jsonResponse([{ id: "categoria-1", nombre: "Aires" }]);
      }
      if (url.endsWith("/equipos/importar") && options.method === "POST") {
        importado = true;
        return jsonResponse({
          creados: 1,
          omitidos: 1,
          errores: [{ fila: 2, error: "Equipo ya existe" }],
        });
      }
      if (url.includes("/equipos/")) {
        return jsonResponse(importado ? [...equiposIniciales, equipoNuevo] : equiposIniciales);
      }

      throw new Error("Solicitud inesperada: " + url);
    }));

    const { container } = render(
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

    await screen.findByText("Equipo existente");
    fireEvent.change(screen.getByLabelText("Filtrar por sede"), {
      target: { value: "sede-1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Importar Excel/CSV" }));

    const archivo = new File(["inventario"], "segunda-importacion.csv", {
      type: "text/csv",
    });
    const inputArchivo = container.querySelector('input[type="file"]');
    fireEvent.change(inputArchivo, { target: { files: [archivo] } });
    expect(screen.getByText("segunda-importacion.csv")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Importar inventario" }));

    expect(await screen.findByText("Importación procesada. Equipos creados: 1. Filas omitidas: 1."))
      .toBeInTheDocument();
    expect(screen.getByText("Fila 2: Equipo ya existe")).toBeInTheDocument();
    expect(screen.getByText("Omitidos:")).toBeInTheDocument();
    expect(screen.getByLabelText("Filtrar por sede")).toHaveValue("");
    expect(inputArchivo).toHaveValue("");
    expect(screen.getByText("Equipo nuevo")).toBeInTheDocument();
  });

  it("muestra responsable y vida útil, filtra por responsable y renderiza historial", async () => {
    const equipo = {
      id: "equipo-1",
      empresa_id: "empresa-1",
      sede_id: "sede-1",
      categoria_id: "categoria-1",
      responsable_id: "usuario-1",
      nombre: "Compresor",
      estado: "OPERATIVO",
      criticidad: "ALTA",
      vida_util_meses: 120,
      activo: true,
    };

    vi.stubGlobal("fetch", vi.fn(async (input) => {
      const url = String(input);
      if (url.endsWith("/empresas/")) return jsonResponse([{ id: "empresa-1", nombre: "Empresa" }]);
      if (url.endsWith("/sedes/")) return jsonResponse([{ id: "sede-1", empresa_id: "empresa-1", nombre: "Sede" }]);
      if (url.endsWith("/categorias/")) return jsonResponse([{ id: "categoria-1", nombre: "Industrial" }]);
      if (url.endsWith("/usuarios/")) return jsonResponse([{ id: "usuario-1", nombre_completo: "Laura Gómez", rol: "EMPRESA" }]);
      if (url.endsWith("/equipos/equipo-1/historial")) return jsonResponse({
        historial_cambios: [{
          timestamp: "2026-08-26T12:00:00Z",
          tipo_movimiento: "ASIGNACION",
          campo: "responsable_id",
          anterior: null,
          nuevo: "usuario-1",
          observacion: "Entrega inicial",
        }],
      });
      if (url.includes("/equipos/")) return jsonResponse([equipo]);
      throw new Error("Solicitud inesperada: " + url);
    }));

    render(
      <AuthContext.Provider value={{ user: { rol: "ADMIN" }, logout: vi.fn() }}>
        <MemoryRouter><EquiposPage /></MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(await screen.findByText("Compresor")).toBeInTheDocument();
    expect(screen.getAllByText("Laura Gómez")).toHaveLength(2);
    fireEvent.change(screen.getByPlaceholderText("Buscar equipos, cámaras, inventario o sede..."), {
      target: { value: "Laura Gómez" },
    });
    expect(screen.getByText("Compresor")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Filtrar por responsable"), { target: { value: "usuario-1" } });
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("responsable_id=usuario-1"),
      expect.any(Object),
    ));
    fireEvent.click(screen.getByTitle("Ver detalle"));
    expect(screen.getByText("120 meses")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Cerrar" }));
    fireEvent.click(screen.getByTitle("Ver historial"));
    expect(await screen.findByText("ASIGNACION")).toBeInTheDocument();
    expect(screen.getByText("responsable_id")).toBeInTheDocument();
    expect(screen.getByText("Entrega inicial")).toBeInTheDocument();
  });

  it("cierra el modal solo cuando el movimiento es exitoso y no envía actor", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    let falla = true;
    vi.stubGlobal("fetch", vi.fn(async (input, options = {}) => {
      const url = String(input);
      if (url.endsWith("/empresas/") || url.endsWith("/sedes/") || url.endsWith("/categorias/")) return jsonResponse([]);
      if (url.endsWith("/usuarios/")) return jsonResponse([{ id: "usuario-1", nombre_completo: "Laura", rol: "EMPRESA" }]);
      if (url.endsWith("/equipos/equipo-1/asignar") && options.method === "POST") {
        if (falla) return { ok: false, json: async () => ({ detail: "Movimiento rechazado" }) };
        return jsonResponse({});
      }
      if (url.includes("/equipos/")) return jsonResponse([{
        id: "equipo-1", nombre: "Compresor", estado: "OPERATIVO", criticidad: "MEDIA", activo: true,
      }]);
      throw new Error("Solicitud inesperada: " + url);
    }));

    render(
      <AuthContext.Provider value={{ user: { rol: "ADMIN" }, logout: vi.fn() }}>
        <MemoryRouter><EquiposPage /></MemoryRouter>
      </AuthContext.Provider>,
    );

    fireEvent.click(await screen.findByTitle("Asignar"));
    fireEvent.change(screen.getByLabelText("Responsable *"), { target: { name: "responsable_id", value: "usuario-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Ejecutar movimiento" }));
    expect(await screen.findByText("Movimiento rechazado")).toBeInTheDocument();
    expect(screen.getByText("Asignar equipo")).toBeInTheDocument();

    falla = false;
    fireEvent.click(screen.getByRole("button", { name: "Ejecutar movimiento" }));
    await waitFor(() => expect(screen.queryByText("Asignar equipo")).not.toBeInTheDocument());
    const movimientos = fetch.mock.calls.filter(([url]) => String(url).endsWith("/asignar"));
    expect(JSON.parse(movimientos.at(-1)[1].body)).toEqual({ responsable_id: "usuario-1", ubicacion: "", observacion: "" });
  });

  it("exporta el inventario desde la cabecera", async () => {
    const createObjectURL = vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:inventario");
    const revokeObjectURL = vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {});
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    vi.stubGlobal("fetch", vi.fn(async (input) => {
      const url = String(input);
      if (url.endsWith("/usuarios/")) return jsonResponse([]);
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
