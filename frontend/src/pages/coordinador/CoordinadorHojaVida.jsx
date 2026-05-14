/*
===========================================================
COORDINADOR — HOJA DE VIDA DE EQUIPOS PRO
Archivo: frontend/src/pages/coordinador/CoordinadorHojaVida.jsx
Permisos usados:
- HOJA_VIDA_VER
- HOJA_VIDA_EDITAR
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { FileText, RefreshCw, Search, Save } from "lucide-react";
import "../../styles/coordinador.css";

export default function CoordinadorHojaVida() {
  const [equipos, setEquipos] = useState([]);
  const [permisos, setPermisos] = useState([]);
  const [equipoId, setEquipoId] = useState("");
  const [hojaVida, setHojaVida] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    if (equipoId) cargarHojaVida(equipoId);
  }, [equipoId]);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      const [resCatalogos, resPermisos] = await Promise.all([
        API.get("/coordinador/catalogos"),
        API.get("/permisos/me"),
      ]);
      setEquipos(resCatalogos.data?.equipos || []);
      setPermisos(resPermisos.data?.permisos_finales || []);
    } catch (error) {
      console.error("Error cargando hoja vida:", error);
      mostrarMensaje("error", "No se pudieron cargar los equipos.");
    } finally {
      setCargando(false);
    }
  };

  const tienePermiso = (...codigos) => codigos.some((c) => permisos.includes(c));
  const puedeVer = tienePermiso("HOJA_VIDA_VER");
  const puedeEditar = tienePermiso("HOJA_VIDA_EDITAR");

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });
    setTimeout(() => setMensaje(null), 3500);
  };

  const equiposFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();
    return equipos.filter((e) => `${e.nombre || ""} ${e.codigo || ""} ${e.codigo_inventario || ""} ${e.serie || ""}`.toLowerCase().includes(texto));
  }, [equipos, busqueda]);

  const cargarHojaVida = async (id) => {
    try {
      setHojaVida(null);
      const res = await API.get(`/equipos/${id}/hoja-vida`);
      setHojaVida(res.data || {});
    } catch (error) {
      console.warn("No existe endpoint /equipos/{id}/hoja-vida o no hay hoja creada:", error);
      const equipo = equipos.find((e) => String(e.id) === String(id));
      setHojaVida({
        equipo_id: id,
        equipo_nombre: equipo?.nombre || equipo?.nombre_completo || "Equipo",
        marca: equipo?.marca || "",
        modelo: equipo?.modelo || "",
        serie: equipo?.serie || "",
        ubicacion: equipo?.ubicacion || "",
        especificaciones_tecnicas: "",
        recomendaciones: "",
        observaciones: "",
      });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setHojaVida((prev) => ({ ...prev, [name]: value }));
  };

  const guardarHojaVida = async () => {
    if (!equipoId || !hojaVida) return;

    try {
      setGuardando(true);
      await API.put(`/equipos/${equipoId}/hoja-vida`, hojaVida);
      mostrarMensaje("success", "Hoja de vida actualizada correctamente.");
    } catch (error) {
      console.error("Error guardando hoja de vida:", error);
      mostrarMensaje("error", "No se pudo guardar. Verifica que exista el endpoint backend de hoja de vida.");
    } finally {
      setGuardando(false);
    }
  };

  if (!puedeVer) return <div className="coord-alert error">No tienes permiso para ver hoja de vida.</div>;

  return (
    <div className="coord-page">
      <div className="coord-page-header">
        <div>
          <span className="coord-eyebrow">Hoja de vida</span>
          <h2>Hoja de vida técnica</h2>
          <p>Consulta y actualiza la información técnica de equipos de la empresa.</p>
        </div>
        <button className="coord-secondary-btn" onClick={cargarDatos}><RefreshCw size={17} /> Actualizar</button>
      </div>

      {mensaje && <div className={`coord-alert ${mensaje.tipo === "error" ? "error" : "success"}`}>{mensaje.texto}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Buscar equipo..." />
        </div>
        <select value={equipoId} onChange={(e) => setEquipoId(e.target.value)}>
          <option value="">Seleccionar equipo</option>
          {equiposFiltrados.map((e) => <option key={e.id} value={e.id}>{e.nombre || e.nombre_completo || e.codigo || e.id}</option>)}
        </select>
      </div>

      {cargando ? (
        <div className="coord-loading">Cargando información...</div>
      ) : !equipoId ? (
        <div className="coord-empty-card"><FileText size={34} /><h3>Selecciona un equipo</h3><p>Elige un equipo para consultar su hoja de vida.</p></div>
      ) : (
        <div className="coord-card">
          <div className="coord-card-header">
            <div>
              <h3>{hojaVida?.equipo_nombre || "Hoja de vida del equipo"}</h3>
              <p>Información técnica y observaciones del equipo.</p>
            </div>
            <FileText size={26} />
          </div>

          <div className="form-pro">
            <div className="form-grid">
              <div className="form-group"><label>Marca</label><input name="marca" value={hojaVida?.marca || ""} onChange={handleChange} disabled={!puedeEditar} /></div>
              <div className="form-group"><label>Modelo</label><input name="modelo" value={hojaVida?.modelo || ""} onChange={handleChange} disabled={!puedeEditar} /></div>
              <div className="form-group"><label>Serie</label><input name="serie" value={hojaVida?.serie || ""} onChange={handleChange} disabled={!puedeEditar} /></div>
              <div className="form-group"><label>Ubicación</label><input name="ubicacion" value={hojaVida?.ubicacion || ""} onChange={handleChange} disabled={!puedeEditar} /></div>
            </div>
            <div className="form-group"><label>Especificaciones técnicas</label><textarea name="especificaciones_tecnicas" rows="4" value={hojaVida?.especificaciones_tecnicas || ""} onChange={handleChange} disabled={!puedeEditar} /></div>
            <div className="form-group"><label>Recomendaciones</label><textarea name="recomendaciones" rows="3" value={hojaVida?.recomendaciones || ""} onChange={handleChange} disabled={!puedeEditar} /></div>
            <div className="form-group"><label>Observaciones</label><textarea name="observaciones" rows="3" value={hojaVida?.observaciones || ""} onChange={handleChange} disabled={!puedeEditar} /></div>

            {puedeEditar && (
              <div className="modal-actions-pro">
                <button className="coord-primary-btn" onClick={guardarHojaVida} disabled={guardando}><Save size={16} /> {guardando ? "Guardando..." : "Guardar hoja de vida"}</button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
