// ============================================================
// LOGIN ULTRA PRO - SGA PRO
// Login empresarial SaaS con redirección por roles
// ============================================================

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, Lock, Mail, ShieldCheck } from "lucide-react";
import API from "../api/axios";
import "../styles/login.css";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.username || !form.password) {
      setError("Ingresa usuario/correo y contraseña.");
      return;
    }

    try {
      setLoading(true);

      const res = await API.post("/auth/login", {
        username: form.username,
        password: form.password,
      });

      const data = res.data;

      localStorage.setItem("token", data.access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          usuario_id: data.usuario_id,
          nombre_completo: data.nombre_completo,
          rol: data.rol,
          empresa_id: data.empresa_id || null,
        })
      );

      if (data.rol === "ADMIN" || data.rol === "COORDINADOR") {
        navigate("/admin");
      } else if (data.rol === "EMPRESA" || data.rol === "CLIENTE") {
        navigate("/cliente/dashboard");
      } else if (data.rol === "TECNICO") {
        navigate("/tecnico");
      } else {
        navigate("/");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Usuario o contraseña incorrectos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-ultra">
      <section className="login-hero">
        <div className="login-glow login-glow-one"></div>
        <div className="login-glow login-glow-two"></div>

        <div className="hero-content">
          <div className="brand-chip">
            <img src="/logo.png" alt="SGA PRO" />
            <div>
              <strong>SGA HOLDING SAS</strong>
              <span>Gestión inteligente de activos</span>
            </div>
          </div>

          <h1>
            Plataforma SaaS para gestión de activos y mantenimiento.
          </h1>

          <p>
            Administra empresas, sedes, inventario, técnicos, mantenimientos,
            evidencias, hojas de vida y trazabilidad en una sola plataforma.
          </p>

          <div className="hero-badges">
            <span>Multiempresa</span>
            <span>Inventario</span>
            <span>Evidencias</span>
            <span>Reportes</span>
          </div>
        </div>
      </section>

      <section className="login-panel">
        <form className="login-card-pro" onSubmit={handleLogin}>
          <div className="login-logo-wrap">
            <img src="/logo.png" alt="SGA PRO" />
          </div>

          <div className="login-title">
            <h2>Bienvenidos</h2>
            <p>Acceso seguro a SGA PRO</p>
          </div>

          {error && <div className="login-error">{error}</div>}

          <label>Usuario o correo electrónico</label>
          <div className="login-input-group">
            <Mail size={18} />
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="admin@sga.com"
              autoComplete="username"
            />
          </div>

          <label>Contraseña</label>
          <div className="login-input-group">
            <Lock size={18} />
            <input
              name="password"
              type={showPassword ? "text" : "password"}
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
              autoComplete="current-password"
            />

            <button
              type="button"
              className="password-eye"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          <button className="login-submit" disabled={loading}>
            {loading ? "Validando acceso..." : "Ingresar"}
          </button>

          <div className="secure-note">
            <ShieldCheck size={16} />
            Sesión protegida · Plataforma empresarial
          </div>
        </form>
      </section>
    </div>
  );
}