// ============================================================
// NO AUTORIZADO PRO
// Archivo: frontend/src/pages/NoAutorizado.jsx
// ============================================================

import { Link } from "react-router-dom";

export default function NoAutorizado() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        background: "#f8fafc",
        fontFamily: "Times New Roman, Times, serif",
      }}
    >
      <section
        style={{
          width: "min(520px, 92vw)",
          background: "white",
          borderRadius: "22px",
          padding: "32px",
          boxShadow: "0 22px 60px rgba(15,23,42,.14)",
          border: "1px solid #e2e8f0",
          textAlign: "center",
        }}
      >
        <h1 style={{ color: "#0f172a", marginBottom: "12px" }}>
          Acceso no autorizado
        </h1>

        <p style={{ color: "#475569", marginBottom: "24px" }}>
          Tu usuario no tiene permisos para ingresar a este módulo.
        </p>

        <Link
          to="/"
          style={{
            display: "inline-block",
            padding: "12px 18px",
            borderRadius: "12px",
            background: "#0f3a75",
            color: "white",
            textDecoration: "none",
            fontWeight: 700,
          }}
        >
          Volver al inicio
        </Link>
      </section>
    </main>
  );
}
