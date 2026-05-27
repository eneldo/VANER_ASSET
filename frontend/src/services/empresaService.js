import axios from "../api/axios";

export const obtenerEmpresa = async () => {
  return await axios.get("/empresas");
};
