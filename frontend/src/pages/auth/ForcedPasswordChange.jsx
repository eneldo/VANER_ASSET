import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, Lock, ShieldCheck } from "lucide-react";
import api from "../../api/axios";
import "../../styles/password-recovery.css";

const POLICY_RULES = [
  { key: "length", test: (p) => p.length >= 15, msg: "Mínimo 15 caracteres" },
  { key: "upper", test: (p) => /[A-Z]/.test(p), msg: "Una mayúscula" },
  { key: "lower", test: (p) => /[a-z]/.test(p), msg: "Una minúscula" },
  { key: "digit", test: (p) => /[0-9]/.test(p), msg: "Un número" },
  { key: "special", test: (p) => /[^A-Za-z0-9\s]/.test(p), msg: "Un carácter especial" },
  { key: "space", test: (p) => p.includes(" "), msg: "Puedes usar espacios (frase)" },
];

const FORBIDDEN = ["vaner", "admin", "123456", "password"];

function getStrength(pw) {
  if (!pw) return 0;
  let score = 0;
  if (pw.length >= 15) score++;
  if (pw.length >= 20) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9\s]/.test(pw)) score++;
  if (pw.includes(" ") && pw.length >= 20) score++;
  const lower = pw.toLowerCase();
  if (FORBIDDEN.some((f) => lower.includes(f))) score = Math.max(score - 2, 0);
  return Math.min(score, 5);
}

function strengthLabel(s) {
  return ["Muy débil", "Débil", "Aceptable", "Buena", "Fuerte", "Muy fuerte"][s] || "";
}

function strengthColor(s) {
  return ["#ef4444", "#f97316", "#eab308", "#22c55e", "#16a34a", "#0f766e"][s] || "#94a3b8";
}

export default function ForcedPasswordChange() {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const score = getStrength(password);
  const rulesPassed = POLICY_RULES.filter((r) => r.test(password)).length;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (password.length < 15) {
      setError("La contraseña debe tener al menos 15 caracteres.");
      return;
    }
    if (password !== confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    try {
      setLoading(true);
      const { data } = await api.post("/usuarios/cambio-password", {
        password_actual: password,
        nueva_password: password,
        confirmar_password: password,
      });
      setSuccess(data.message || "Contraseña actualizada correctamente.");
      setTimeout(() => navigate("/", { replace: true }), 1500);
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
        <h1>Cambio de contraseña requerido</h1>
        <p>Tu contraseña temporal ha expirado o es tu primer acceso. Debes crear una contraseña nueva.</p>

        {success && <div className="recovery-success">{success}</div>}
        {error && <div className="recovery-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <label htmlFor="new-password">Nueva contraseña</label>
          <div className="recovery-input">
            <Lock size={18} />
            <input
              id="new-password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mínimo 15 caracteres"
              autoComplete="new-password"
              minLength={15}
              maxLength={128}
              required
            />
            <button
              type="button"
              className="recovery-eye"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {password && (
            <div className="password-strength">
              <div className="strength-bar">
                <div
                  className="strength-fill"
                  style={{ width: `${(score / 5) * 100}%`, background: strengthColor(score) }}
                />
              </div>
              <span className="strength-label" style={{ color: strengthColor(score) }}>
                {strengthLabel(score)} — {rulesPassed}/{POLICY_RULES.length} requisitos
              </span>
              <ul className="strength-rules">
                {POLICY_RULES.map((r) => (
                  <li key={r.key} className={r.test(password) ? "passed" : ""}>
                    {r.test(password) ? "✓" : "○"} {r.msg}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <label htmlFor="confirm-password">Confirmar contraseña</label>
          <div className="recovery-input">
            <Lock size={18} />
            <input
              id="confirm-password"
              type={showPassword ? "text" : "password"}
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              placeholder="Repite la contraseña"
              autoComplete="new-password"
              minLength={15}
              maxLength={128}
              required
            />
          </div>
          {confirm && password !== confirm && (
            <p className="field-error">Las contraseñas no coinciden.</p>
          )}

          <button type="submit" disabled={loading || score < 3}>
            {loading ? "Guardando..." : "Guardar contraseña"}
          </button>
        </form>
      </section>
    </main>
  );
}
