// ============================================================
// RESET PASSWORD - FASE 31.7
// Archivo: frontend/src/pages/auth/ResetPassword.jsx
// ============================================================

import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Eye, EyeOff, Lock, ShieldCheck } from "lucide-react";
import api from "../../api/axios";
import "../../styles/password-recovery.css";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get("token") || "";

  const [validating, setValidating] = useState(true);
  const [valid, setValid] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const validate = async () => {
      if (!token) {
        setError("Token no encontrado.");
        setValidating(false);
        return;
      }

      try {
        const { data } = await api.get(`/auth/reset-password/validate?token=${encodeURIComponent(token)}`);
        setValid(Boolean(data.valid));
        setEmail(data.email || "");
      } catch (err) {
        setError(err.response?.data?.detail || "El enlace es inválido o expiró.");
      } finally {
        setValidating(false);
      }
    };

    validate();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (password.length < 8) {
      setError("La contraseña debe tener mínimo 8 caracteres.");
      return;
    }

    if (password !== confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    try {
      setLoading(true);
      const { data } = await api.post("/auth/reset-password", {
        token,
        new_password: password,
      });
      setMessage(data.message || "Contraseña actualizada correctamente.");
      setTimeout(() => navigate("/login", { replace: true }), 1600);
    } catch (err) {
      setError(err.response?.data?.detail || "No fue posible actualizar la contraseña.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="recovery-page">
      <section className="recovery-card">
        <div className="recovery-icon"><ShieldCheck size={34} /></div>
        <h1>Nueva contraseña</h1>
        <p>{email ? `Cuenta: ${email}` : "Crea una nueva contraseña segura para tu cuenta."}</p>

        {validating && <div className="recovery-info">Validando enlace...</div>}
        {message && <div className="recovery-success">{message}</div>}
        {error && <div className="recovery-error">{error}</div>}

        {!validating && valid && (
          <form onSubmit={handleSubmit}>
            <label>Nueva contraseña</label>
            <div className="recovery-input">
              <Lock size={18} />
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mínimo 8 caracteres"
                autoComplete="new-password"
              />
              <button
                type="button"
                className="recovery-eye"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <label>Confirmar contraseña</label>
            <div className="recovery-input">
              <Lock size={18} />
              <input
                type={showPassword ? "text" : "password"}
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                placeholder="Repite la contraseña"
                autoComplete="new-password"
              />
            </div>

            <button disabled={loading}>{loading ? "Guardando..." : "Guardar contraseña"}</button>
          </form>
        )}

        <Link className="recovery-link" to="/login">Volver al login</Link>
      </section>
    </main>
  );
}
