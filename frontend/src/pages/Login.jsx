// ============================================================
// LOGIN ULTRA PRO - VANER ASSET
// Archivo: frontend/src/pages/Login.jsx
// ============================================================

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, Lock, Mail, ShieldCheck, Building2, Package, Wrench, ClipboardList, BarChart3 } from "lucide-react";

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
      <section className="login-panel">
        <form className="login-card-pro" onSubmit={handleLogin}>
          <div className="login-logo-wrap">
            <img src={PRODUCT.logoUrl} alt={PRODUCT.productName} />
          </div>

          <div className="login-title">
            <h2>Bienvenido</h2>
            <p>Acceso seguro a {PRODUCT.productName}</p>
          </div>

          {error && <div className="login-error">{error}</div>}

          <label>Usuario o correo electrónico</label>
          <div className="login-input-group">
            <Mail size={16} />
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
            <Lock size={16} />
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
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>

          <button className="login-submit" disabled={loading}>
            {loading ? "Validando acceso..." : "Ingresar"}
          </button>

          <div className="secure-note">
            <ShieldCheck size={14} />
            Sesión protegida · Plataforma empresarial
          </div>

          <div className="login-footer">
            Elaborado por Eneldo Vanstralhen Ingeniero de Sistemas
          </div>
        </form>
      </section>

      <section className="login-hero">
        <div className="login-glow login-glow-one"></div>
        <div className="login-glow login-glow-two"></div>

        <div className="hero-content">
          <div className="brand-chip">
            <img src={PRODUCT.logoUrl} alt={PRODUCT.productName} />
            <div>
              <strong>{PRODUCT.productName}</strong>
              <span>{PRODUCT.clientName}</span>
            </div>
          </div>

          <h1>Control inteligente de activos y mantenimiento.</h1>

          <p>
            Centraliza inventarios, activos, órdenes de trabajo y mantenimiento
            con trazabilidad multiempresa.
          </p>

          <div className="hero-badges">
            <span><Building2 size={16} /> Multiempresa</span>
            <span><Package size={16} /> Inventario</span>
            <span><ClipboardList size={16} /> Activos</span>
            <span><Wrench size={16} /> Mantenimiento</span>
            <span><BarChart3 size={16} /> Reportes</span>
          </div>
        </div>
      </section>
    </div>
  );
}
