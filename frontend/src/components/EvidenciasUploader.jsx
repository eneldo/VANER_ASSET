// ============================================================
// COMPONENTE EVIDENCIAS PRO
// ============================================================

import { useState } from "react";
import API from "../api/axios";
import { UploadCloud, Image, FileText } from "lucide-react";

export default function EvidenciasUploader({ mantenimientoId, equipoId }) {
  const [archivo, setArchivo] = useState(null);
  const [tipo, setTipo] = useState("ANTES");
  const [descripcion, setDescripcion] = useState("");

  const subir = async () => {
    if (!archivo) return alert("Selecciona archivo");

    const formData = new FormData();
    formData.append("archivo", archivo);
    formData.append("mantenimiento_id", mantenimientoId);
    formData.append("equipo_id", equipoId);
    formData.append("tipo", tipo);
    formData.append("descripcion", descripcion);

    try {
      await API.post("/evidencias/subir", formData);
      alert("Evidencia subida");
    } catch (error) {
      console.error(error);
      alert("Error subiendo evidencia");
    }
  };

  return (
    <div style={styles.card}>
      <h3>Subir evidencia</h3>

      <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
        <option value="ANTES">Antes</option>
        <option value="DESPUES">Después</option>
        <option value="SOPORTE">Soporte</option>
      </select>

      <input type="file" onChange={(e) => setArchivo(e.target.files[0])} />

      <input
        placeholder="Descripción"
        value={descripcion}
        onChange={(e) => setDescripcion(e.target.value)}
      />

      <button onClick={subir}>
        <UploadCloud size={16} /> Subir
      </button>
    </div>
  );
}

const styles = {
  card: {
    border: "1px solid #e2e8f0",
    padding: 16,
    borderRadius: 12,
    background: "white",
  },
};