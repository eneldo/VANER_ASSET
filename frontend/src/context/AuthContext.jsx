// =========================================================
// AUTH CONTEXT SGA PRO (CORREGIDO)
// Manejo de sesión + almacenamiento completo del usuario
// =========================================================

import { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(
    JSON.parse(localStorage.getItem("user")) || null
  );

  const login = (data) => {
    // 👉 GUARDAMOS TODO EL USER INCLUYENDO empresa_id
    const userData = {
      usuario_id: data.usuario_id,
      nombre_completo: data.nombre_completo,
      rol: data.rol,
      empresa_id: data.empresa_id, // 🔥 CLAVE
    };

    localStorage.setItem("user", JSON.stringify(userData));
    localStorage.setItem("token", data.access_token);

    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    setUser(null);
    window.location.href = "/";
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};