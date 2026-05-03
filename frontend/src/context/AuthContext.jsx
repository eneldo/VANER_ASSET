// =========================================================
// CONTEXTO DE AUTENTICACIÓN
// Maneja login, logout y usuario global
// =========================================================

import { createContext, useState } from "react";
import API from "../api/axios";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(
    JSON.parse(localStorage.getItem("user"))
  );

  const login = async (username, password) => {
    try {
      const res = await API.post("/auth/login", {
        username,
        password,
      });

      const data = res.data;

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data));

      setUser(data);

      return data;
    } catch (error) {
      throw error.response?.data?.detail || "Error login";
    }
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};