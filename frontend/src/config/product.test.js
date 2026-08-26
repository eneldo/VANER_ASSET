import { describe, expect, it } from "vitest";

import { createProductConfig } from "./product";
import { loadRuntimeConfig, normalizeRuntimeConfig } from "./runtime";


describe("configuración CORE y cliente", () => {
  it("mantiene identidad CORE separada del cliente", () => {
    const runtime = normalizeRuntimeConfig({
      appName: "VANER ASSET",
      clientCode: "empresa_xyz",
      clientName: "Empresa XYZ S.A.S.",
      appDomain: "asset.empresaxyz.com",
      coreCompanyName: "VANER SOFTWARE",
      coreProductName: "VANER ASSET",
    });

    const product = createProductConfig(runtime);

    expect(product.companyName).toBe("VANER SOFTWARE");
    expect(product.clientCode).toBe("empresa_xyz");
    expect(product.organizationName).toBe("Empresa XYZ S.A.S.");
    expect(product.appDomain).toBe("asset.empresaxyz.com");
  });

  it("carga la identidad del cliente desde el endpoint público", async () => {
    const fetchMock = async (url) => ({
      ok: true,
      json: async () => ({
        appName: "VANER ASSET",
        clientCode: "cliente_runtime",
        clientName: "Cliente Runtime S.A.S.",
        appDomain: "asset.cliente.test",
      }),
      requestedUrl: url,
    });

    const config = await loadRuntimeConfig(fetchMock);

    expect(config.clientCode).toBe("cliente_runtime");
    expect(document.documentElement.dataset.clientCode).toBe("cliente_runtime");
    expect(document.title).toBe("VANER ASSET | Cliente Runtime S.A.S.");
  });
});
