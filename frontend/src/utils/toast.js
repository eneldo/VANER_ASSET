const TOAST_EVENT = "sga:toast";

export function showToast(message, type = "info", duration = 4000) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent(TOAST_EVENT, {
      detail: {
        id: crypto.randomUUID?.() || String(Date.now()) + "-" + String(Math.random()),
        message: String(message || ""),
        type,
        duration,
      },
    }),
  );
}

export function installAlertBridge() {
  if (typeof window === "undefined" || window.__sgaAlertBridgeInstalled) return;
  window.__sgaAlertBridgeInstalled = true;
  window.alert = (message) => showToast(message, "warning", 5000);
}

export { TOAST_EVENT };
