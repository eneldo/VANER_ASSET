import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";

// ============================================================
// ESTILOS BASE DEL SISTEMA
// ============================================================
import "./index.css";
import "./styles/session-security.css";

// ============================================================
// FASE 32.3 - RESPONSIVE GLOBAL REAL
// Estos archivos deben cargarse después de estilos base.
// ============================================================
import "./styles/responsive-global.css";
import "./styles/admin-responsive-fixes.css";
import "./styles/cliente-responsive-fixes.css";
import "./styles/tecnico-responsive-fixes.css";
import "./styles/coordinador-responsive-fixes.css";

// ============================================================
// FASE 32.4 - OPTIMIZACIÓN MÓDULO POR MÓDULO
// Estos archivos se cargan al final para corregir módulos existentes
// sin reescribir cada página todavía.
// ============================================================
import "./styles/fase32_4/modulos-pro.css";
import "./styles/fase32_4/tablas-pro.css";
import "./styles/fase32_4/formularios-pro.css";
import "./styles/fase32_4/modulos-admin-pro.css";
import "./styles/fase32_4/modulos-cliente-pro.css";
import "./styles/fase32_4/modulos-tecnico-pro.css";
import "./styles/fase32_4/modulos-coordinador-pro.css";
import "./styles/fase32_4/print-fixes.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
