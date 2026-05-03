import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const data = await login(form.username, form.password);

      // Redirección por rol
      if (data.rol === "TECNICO") {
        navigate("/tecnico");
      } else if (data.rol === "ADMIN") {
        navigate("/admin");
      } else {
        navigate("/");
      }

    } catch (err) {
      alert(err);
    }
  };

  return (
    <div style={{ padding: 50 }}>
      <h2>Login SGA PRO</h2>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Usuario"
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

        <button type="submit">Ingresar</button>
      </form>
    </div>
  );
}