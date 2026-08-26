import { getRuntimeConfig } from "./runtime";


export function createProductConfig(runtime = getRuntimeConfig()) {
  return {
    companyName: runtime.coreCompanyName,
    productName: runtime.appName,
    coreProductName: runtime.coreProductName,
    clientCode: runtime.clientCode,
    clientName: runtime.clientName,
    organizationName: runtime.clientName || runtime.coreCompanyName,
    appDomain: runtime.appDomain,
    shortName: "VA",
    description: runtime.description,
    logoUrl: "/vaner-asset-logo.svg",
    modules: Object.freeze([
      "Inventarios",
      "Activos",
      "Mantenimiento",
      "Órdenes de trabajo",
      "Repuestos",
      "Técnicos",
      "Reportes",
      "Dashboard",
      "Administración",
    ]),
  };
}


export const PRODUCT = Object.freeze(createProductConfig());
