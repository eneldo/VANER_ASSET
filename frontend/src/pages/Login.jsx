// =========================================================
// LOGIN PAGE SGA PRO (CORREGIDO)
// Guarda correctamente empresa_id
// =========================================================

import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";
import { AuthContext } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const handleLogin = async () => {
    try {
      const res = await API.post("/auth/login", form);

      console.log("LOGIN RESPONSE:", res.data); // DEBUG

      // 👉 GUARDAMOS TODO
      login(res.data);

      // 👉 REDIRECCIÓN SEGÚN ROL
      if (res.data.rol === "ADMIN") {
        navigate("/admin");
      } else if (res.data.rol === "TECNICO") {
        navigate("/tecnico");
      } else if (res.data.rol === "EMPRESA") {
        navigate("/cliente/dashboard");
      }

    } catch (error) {
      alert("Error en login");
      console.error(error);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>SGA PRO</h2>

        <input
          placeholder="Usuario o correo"
          onChange={(e) =>
            setForm({ ...form, username: e.target.value })
          }
        />

        <input
          type="password"
          placeholder="Contraseña"
          onChange={(e) =>
            setForm({ ...form, password: e.target.value })
          }
        />

        <button onClick={handleLogin}>
          Ingresar
        </button>
      </div>
    </div>
  );
}

// =========================================================
// ESTILOS
// =========================================================

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f5f8ff",
  },
  card: {
    background: "white",
    padding: 30,
    borderRadius: 12,
    display: "flex",
    flexDirection: "column",
    gap: 10,
    width: 300,
  },
};