// ============================================================
// SESSION TIMEOUT PRO
// Archivo: frontend/src/hooks/useSessionTimeout.js
// ============================================================
// Cierra sesión por inactividad.
// Uso recomendado en App.jsx o AdminLayout.jsx:
// useSessionTimeout({ minutes: 30 });
// ============================================================

import { useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";

export function useSessionTimeout({ minutes = 30 } = {}) {
  const { logout, isAuthenticated } = useAuth();
  const timerRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated) return;

    const timeoutMs = minutes * 60 * 1000;

    const resetTimer = () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }

      timerRef.current = setTimeout(() => {
        alert("Tu sesión fue cerrada por inactividad.");
        logout();
      }, timeoutMs);
    };

    const events = ["mousemove", "keydown", "click", "scroll", "touchstart"];

    events.forEach((event) => window.addEventListener(event, resetTimer));
    resetTimer();

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }

      events.forEach((event) => window.removeEventListener(event, resetTimer));
    };
  }, [isAuthenticated, logout, minutes]);
}
