import { createContext, useContext } from "react";

export const EmpresaContext = createContext();

export const useEmpresa = () => {
  return useContext(EmpresaContext);
};
