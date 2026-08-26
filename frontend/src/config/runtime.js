const DEFAULT_RUNTIME_CONFIG = Object.freeze({
  appName: "VANER ASSET",
  clientCode: "local",
  clientName: "",
  appDomain: "localhost",
  coreCompanyName: "VANER SOFTWARE",
  coreProductName: "VANER ASSET",
  description: "Plataforma para la gestión de inventarios, activos y mantenimiento.",
});

export function normalizeRuntimeConfig(payload = {}) {
  return Object.freeze({
    appName: String(payload.appName || DEFAULT_RUNTIME_CONFIG.appName).trim(),
    clientCode: String(payload.clientCode || DEFAULT_RUNTIME_CONFIG.clientCode).trim(),
    clientName: String(payload.clientName || "").trim(),
    appDomain: String(payload.appDomain || DEFAULT_RUNTIME_CONFIG.appDomain).trim(),
    coreCompanyName: String(
      payload.coreCompanyName || DEFAULT_RUNTIME_CONFIG.coreCompanyName,
    ).trim(),
    coreProductName: String(
      payload.coreProductName || DEFAULT_RUNTIME_CONFIG.coreProductName,
    ).trim(),
    description: String(payload.description || DEFAULT_RUNTIME_CONFIG.description).trim(),
  });
}

export function getRuntimeConfig() {
  return globalThis.__VANER_RUNTIME_CONFIG__ || DEFAULT_RUNTIME_CONFIG;
}

export function applyRuntimeMetadata(config) {
  if (typeof document === "undefined") return;

  document.documentElement.dataset.clientCode = config.clientCode;
  document.title = config.clientName
    ? `${config.appName} | ${config.clientName}`
    : `${config.appName} | ${config.coreCompanyName}`;

  const description = document.querySelector('meta[name="description"]');
  if (description) description.setAttribute("content", config.description);
}

export async function loadRuntimeConfig(fetchImpl = globalThis.fetch) {
  const apiBase = (import.meta.env.VITE_API_URL || "/api").replace(/\/$/, "");
  let config = DEFAULT_RUNTIME_CONFIG;

  try {
    const response = await fetchImpl(`${apiBase}/public/config`, {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    config = normalizeRuntimeConfig(await response.json());
  } catch (error) {
    console.warn("No fue posible cargar la configuración pública; se usará el CORE.", error);
  }

  globalThis.__VANER_RUNTIME_CONFIG__ = config;
  applyRuntimeMetadata(config);
  return config;
}
