// ============================================================
// FORGOT PASSWORD - FASE 31.7
// Archivo: frontend/src/pages/auth/ForgotPassword.jsx
// ============================================================

import { useState } from "react";
import { Link } from "react-router-dom";
import { Mail, ShieldCheck } from "lucide-react";
import api from "../../api/axios";
import "../../styles/password-recovery.css";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!email.trim()) {
      setError("Ingresa tu correo electrónico.");
      return;
    }

    try {
      setLoading(true);
      const { data } = await api.post("/auth/forgot-password", {
        email: email.trim(),
      });
      setMessage(data.message || "Revisa tu correo electrónico.");
    } catch (err) {
      setError(err.response?.data?.detail || "No fue posible procesar la solicitud.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="recovery-page">
      <section className="recovery-card">
        <div className="recovery-icon"><ShieldCheck size={34} /></div>
        <h1>Recuperar contraseña</h1>
        <p>Ingresa tu correo y te enviaremos un enlace temporal para crear una nueva contraseña.</p>

        {message && <div className="recovery-success">{message}</div>}
        {error && <div className="recovery-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <label>Correo electrónico</label>
          <div className="recovery-input">
            <Mail size={18} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@vanerasset.com"
              autoComplete="email"
            />
          </div>

          <button disabled={loading}>{loading ? "Enviando..." : "Enviar enlace"}</button>
        </form>

        <Link className="recovery-link" to="/login">Volver al login</Link>
      </section>
    </main>
  );
}
