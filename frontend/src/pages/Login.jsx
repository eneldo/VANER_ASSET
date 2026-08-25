// ============================================================
// LOGIN ULTRA PRO - SGAHolding
// Archivo: frontend/src/pages/Login.jsx
// ============================================================
// Login empresarial SaaS:
// - usa AuthContext.login()
// - evita doble petición al backend
// - guarda access_token / refresh_token desde AuthContext
// - redirecciona por rol
// ============================================================

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, Lock, Mail, ShieldCheck } from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { PRODUCT } from "../config/product";

import "../styles/login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

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

    if (!form.username.trim() || !form.password.trim()) {
      setError("Ingresa usuario/correo y contraseña.");
      return;
    }

    try {
      setLoading(true);

      // ======================================================
      // Login centralizado desde AuthContext
      // Evita doble POST /auth/login
      // ======================================================
      const user = await login({
        username: form.username.trim(),
        password: form.password,
      });

      const rol = user?.rol?.toUpperCase();

      if (rol === "ADMIN") {
        navigate("/admin/dashboard", { replace: true });
      } else if (rol === "COORDINADOR") {
        navigate("/coordinador/dashboard", { replace: true });
      } else if (rol === "EMPRESA" || rol === "CLIENTE") {
        navigate("/cliente/dashboard", { replace: true });
      } else if (rol === "TECNICO") {
        navigate("/tecnico/dashboard", { replace: true });
      } else {
        navigate("/", { replace: true });
      }
    } catch (err) {
      console.error("Error login:", err);
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
            <img src={PRODUCT.logoUrl} alt={PRODUCT.productName} />
            <div>
              <strong>{PRODUCT.productName}</strong>
              <span>{PRODUCT.companyName}</span>
            </div>
          </div>

          <h1>{PRODUCT.description}</h1>

          <p>
            Administra inventarios, activos, órdenes de trabajo, repuestos,
            técnicos y trazabilidad multiempresa en una sola plataforma.
          </p>

          <div className="hero-badges">
            <span>Multiempresa</span>
            <span>Inventario</span>
            <span>Activos</span>
            <span>Mantenimiento</span>
            <span>Reportes</span>
          </div>
        </div>
      </section>

      <section className="login-panel">
        <form className="login-card-pro" onSubmit={handleLogin}>
          <div className="login-logo-wrap">
            <img src={PRODUCT.logoUrl} alt={PRODUCT.productName} />
          </div>

          <div className="login-title">
            <h2>Bienvenidos</h2>
            <p>Acceso seguro a {PRODUCT.productName}</p>
          </div>

          {error && <div className="login-error">{error}</div>}

          <label>Usuario o correo electrónico</label>
          <div className="login-input-group">
            <Mail size={18} />
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="admin@vanerasset.com"
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
