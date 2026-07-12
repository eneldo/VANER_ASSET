import { useEffect, useState } from "react";
import { pendingOfflineCount, syncOfflineQueue } from "../utils/offlineQueue";

export default function OfflineStatus() {
  const [online, setOnline] = useState(navigator.onLine);
  const [pending, setPending] = useState(0);

  useEffect(() => {
    const refreshPending = () => pendingOfflineCount().then(setPending).catch(() => {});
    const handleOnline = () => {
      setOnline(true);
      syncOfflineQueue().then(refreshPending).catch(() => {});
    };
    const handleOffline = () => setOnline(false);

    refreshPending();
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    window.addEventListener("sga:offline-queued", refreshPending);
    window.addEventListener("sga:offline-synced", refreshPending);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("sga:offline-queued", refreshPending);
      window.removeEventListener("sga:offline-synced", refreshPending);
    };
  }, []);

  if (online && pending === 0) return null;

  return (
    <div className={`offline-status ${online ? "syncing" : "offline"}`} role="status" aria-live="polite">
      {online
        ? `Sincronizando ${pending} operación${pending === 1 ? "" : "es"} pendiente${pending === 1 ? "" : "s"}…`
        : `Sin conexión · ${pending} operación${pending === 1 ? "" : "es"} pendiente${pending === 1 ? "" : "s"}`}
    </div>
  );
}
