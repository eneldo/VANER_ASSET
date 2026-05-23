// ============================================================
// COMPONENTE EVIDENCIAS PRO
// Archivo: frontend/src/components/EvidenciasUploader.jsx
// ============================================================

import { useState } from "react";
import API from "../api/axios";
import { UploadCloud } from "lucide-react";

export default function EvidenciasUploader({
  mantenimientoId,
  equipoId,
  onUploaded,
}) {
  const [archivo, setArchivo] = useState(null);
  const [tipo, setTipo] = useState("ANTES");
  const [descripcion, setDescripcion] = useState("");
  const [subiendo, setSubiendo] = useState(false);

  const subir = async () => {
    if (!archivo) {
      alert("Selecciona un archivo.");
      return;
    }

    try {
      setSubiendo(true);

      const formData = new FormData();
      formData.append("archivo", archivo);

      if (mantenimientoId) {
        formData.append("mantenimiento_id", mantenimientoId);
      }

      if (equipoId) {
        formData.append("equipo_id", equipoId);
      }

      formData.append("tipo", tipo);
      formData.append("descripcion", descripcion || "");

      await API.post("/evidencias/subir", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      alert("Evidencia subida correctamente.");

      setArchivo(null);
      setTipo("ANTES");
      setDescripcion("");

      if (typeof onUploaded === "function") {
        onUploaded();
      }
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "Error subiendo evidencia.");
    } finally {
      setSubiendo(false);
    }
  };

  return (
    <div style={styles.card}>
      <h3 style={styles.title}>Subir evidencia</h3>

      <select
        value={tipo}
        onChange={(e) => setTipo(e.target.value)}
        style={styles.input}
      >
        <option value="ANTES">Antes</option>
        <option value="DURANTE">Durante</option>
        <option value="DESPUES">Después</option>
        <option value="SOPORTE">Soporte</option>
      </select>

      <input
        type="file"
        accept="image/*,.pdf"
        onChange={(e) => setArchivo(e.target.files?.[0] || null)}
        style={styles.input}
      />

      <input
        placeholder="Descripción"
        value={descripcion}
        onChange={(e) => setDescripcion(e.target.value)}
        style={styles.input}
      />

      <button onClick={subir} disabled={subiendo} style={styles.button}>
        <UploadCloud size={16} />
        {subiendo ? "Subiendo..." : "Subir evidencia"}
      </button>
    </div>
  );
}

const styles = {
  card: {
    border: "1px solid #e2e8f0",
    padding: 16,
    borderRadius: 16,
    background: "white",
    display: "grid",
    gap: 10,
  },

  title: {
    margin: 0,
    color: "#0f172a",
    fontWeight: 900,
  },

  input: {
    width: "100%",
    border: "1px solid #dbeafe",
    borderRadius: 12,
    padding: "10px 12px",
    outline: "none",
  },

  button: {
    border: "none",
    borderRadius: 12,
    padding: "10px 14px",
    background: "linear-gradient(135deg, #2563eb, #06b6d4)",
    color: "#ffffff",
    fontWeight: 900,
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
};