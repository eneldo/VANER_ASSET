import { useEffect, useState } from "react";
import { CheckCircle2, Info, ShieldAlert, X, XCircle } from "lucide-react";

import { TOAST_EVENT } from "../utils/toast";
import "../styles/toast.css";

const ICONS = {
  success: CheckCircle2,
  error: XCircle,
  warning: ShieldAlert,
  info: Info,
};

export default function ToastViewport() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const timers = new Map();
    const remove = (id) => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
      const timer = timers.get(id);
      if (timer) window.clearTimeout(timer);
      timers.delete(id);
    };
    const onToast = (event) => {
      const toast = event.detail;
      setToasts((current) => [...current.slice(-3), toast]);
      timers.set(toast.id, window.setTimeout(() => remove(toast.id), toast.duration));
    };

    window.addEventListener(TOAST_EVENT, onToast);
    return () => {
      window.removeEventListener(TOAST_EVENT, onToast);
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, []);

  return (
    <div className="toast-viewport" aria-live="polite" aria-atomic="false">
      {toasts.map((toast) => {
        const Icon = ICONS[toast.type] || Info;
        return (
          <div key={toast.id} className={["toast-item", toast.type].join(" ")} role={toast.type === "error" ? "alert" : "status"}>
            <Icon size={20} aria-hidden="true" />
            <span>{toast.message}</span>
            <button
              type="button"
              aria-label="Cerrar notificación"
              onClick={() => setToasts((current) => current.filter((item) => item.id !== toast.id))}
            >
              <X size={17} aria-hidden="true" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
