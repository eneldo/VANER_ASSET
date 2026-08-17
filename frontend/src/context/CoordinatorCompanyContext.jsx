import { createContext, useContext } from "react";

export const CoordinatorCompanyContext = createContext(null);

export function useCoordinatorCompany() {
  const context = useContext(CoordinatorCompanyContext);
  if (!context) {
    throw new Error("useCoordinatorCompany debe usarse dentro de CoordinadorLayout");
  }
  return context;
}
