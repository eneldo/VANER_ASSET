import API from "../api/axios";

const DB_NAME = "sga-offline";
const STORE_NAME = "pending-requests";
const DB_VERSION = 1;

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function formDataToEntries(formData) {
  return Array.from(formData.entries()).map(([key, value]) => ({ key, value }));
}

function entriesToFormData(entries) {
  const data = new FormData();
  entries.forEach(({ key, value }) => data.append(key, value));
  return data;
}

export async function queueOfflineRequest({ method, url, data }) {
  const db = await openDatabase();
  const item = {
    id: crypto.randomUUID(),
    method: method.toLowerCase(),
    url,
    createdAt: new Date().toISOString(),
    attempts: 0,
    isFormData: data instanceof FormData,
    data: data instanceof FormData ? await formDataToEntries(data) : data,
  };

  await new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readwrite");
    transaction.objectStore(STORE_NAME).add(item);
    transaction.oncomplete = resolve;
    transaction.onerror = () => reject(transaction.error);
  });

  if ("serviceWorker" in navigator) {
    const registration = await navigator.serviceWorker.ready;
    if (registration.sync) await registration.sync.register("vaner-asset-sync");
  }

  window.dispatchEvent(new CustomEvent("sga:offline-queued", { detail: item }));
  return item;
}

export async function syncOfflineQueue() {
  if (!navigator.onLine) return { synced: 0, pending: await pendingOfflineCount() };

  const db = await openDatabase();
  const items = await new Promise((resolve, reject) => {
    const request = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).getAll();
    request.onsuccess = () => resolve(request.result.sort((a, b) => a.createdAt.localeCompare(b.createdAt)));
    request.onerror = () => reject(request.error);
  });

  let synced = 0;
  for (const item of items) {
    try {
      const data = item.isFormData ? entriesToFormData(item.data) : item.data;
      await API.request({ method: item.method, url: item.url, data, headers: { "X-Idempotency-Key": item.id } });
      await deleteItem(db, item.id);
      synced += 1;
    } catch (error) {
      if (!error.response || error.response.status >= 500) break;
      await deleteItem(db, item.id);
      window.dispatchEvent(new CustomEvent("sga:offline-rejected", { detail: { item, status: error.response.status } }));
    }
  }

  const pending = await pendingOfflineCount();
  window.dispatchEvent(new CustomEvent("sga:offline-synced", { detail: { synced, pending } }));
  return { synced, pending };
}

function deleteItem(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readwrite");
    transaction.objectStore(STORE_NAME).delete(id);
    transaction.oncomplete = resolve;
    transaction.onerror = () => reject(transaction.error);
  });
}

export async function pendingOfflineCount() {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const request = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).count();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export function isNetworkError(error) {
  return !error?.response || !navigator.onLine;
}
