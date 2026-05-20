import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";

// ============================================================
// ESTILOS GLOBALES DEL SISTEMA
// ============================================================
import "./index.css";
import "./styles/session-security.css";

// ============================================================
// FASE 32.3 - RESPONSIVE GLOBAL REAL
// Estos archivos deben cargarse al final para sobrescribir estilos antiguos
// ============================================================
import "./styles/responsive-global.css";
import "./styles/admin-responsive-fixes.css";
import "./styles/cliente-responsive-fixes.css";
import "./styles/tecnico-responsive-fixes.css";
import "./styles/coordinador-responsive-fixes.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);