/*
FASE 31.6 - MULTIEMPRESA SEGURA PRO
Archivo: frontend/src/components/security/EmpresaScopeGuard.jsx

Objetivo:
- Evitar mostrar pantallas cliente si el usuario no tiene empresa_id.
- No reemplaza la seguridad backend; solo mejora experiencia de usuario.
*/

import { getEmpresaId, isClienteLike } from "../../utils/multiempresa";

export default function EmpresaScopeGuard({ children }) {
  const empresaId = getEmpresaId();

  if (isClienteLike() && !empresaId) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>Empresa no asignada</h2>
        <p>
          Tu usuario tiene rol de cliente, pero no tiene una empresa vinculada.
          Solicita al administrador asignar una empresa al usuario.
        </p>
      </div>
    );
  }

  return children;
}
