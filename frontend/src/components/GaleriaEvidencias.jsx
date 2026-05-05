import { useEffect, useState } from "react";
import API from "../api/axios";

export default function GaleriaEvidencias({ equipoId }) {
  const [imagenes, setImagenes] = useState([]);

  useEffect(() => {
    cargar();
  }, []);

  const cargar = async () => {
    const res = await API.get(`/evidencias/equipo/${equipoId}`);
    setImagenes(res.data);
  };

  return (
    <div>
      <h3>Galería de evidencias</h3>

      <div style={styles.grid}>
        {imagenes.map((img) => (
          <div key={img.id} style={styles.card}>
            {img.archivo_url.includes(".pdf") ? (
              <a href={img.archivo_url} target="_blank">Ver PDF</a>
            ) : (
              <img src={img.archivo_url} style={styles.img} />
            )}

            <span>{img.tipo}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 10,
  },
  card: {
    border: "1px solid #e2e8f0",
    padding: 10,
  },
  img: {
    width: "100%",
    height: 120,
    objectFit: "cover",
  },
};