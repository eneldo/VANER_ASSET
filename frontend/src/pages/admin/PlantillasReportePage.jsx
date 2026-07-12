import { useEffect, useState } from "react";
import { FileCog, Pencil, Plus, Trash2 } from "lucide-react";
import API from "../../api/axios";
import AdminLayout from "./AdminLayout";
import "../../styles/plantillas-reporte.css";

const INICIAL = {
  empresa_id: "", nombre: "Plantilla corporativa", tipo: "AMBOS",
  titulo: "REPORTE DE MANTENIMIENTO", color_primario: "#1E3A8A", pie_pagina: "",
  incluir_logo: true, incluir_evidencias: true, incluir_firmas: true, incluir_costos: false, activo: true,
};

export default function PlantillasReportePage() {
  const [items, setItems] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [form, setForm] = useState(INICIAL);
  const [editId, setEditId] = useState(null);
  const [guardando, setGuardando] = useState(false);

  const cargar = async () => {
    const [plantillas, empresasRes] = await Promise.all([API.get("/plantillas-reporte/"), API.get("/empresas/")]);
    setItems(plantillas.data || []); setEmpresas(empresasRes.data || []);
  };
  useEffect(() => { const timer = setTimeout(() => cargar().catch(console.error), 0); return () => clearTimeout(timer); }, []);

  const guardar = async (event) => {
    event.preventDefault(); setGuardando(true);
    const payload = { ...form, empresa_id: form.empresa_id || null };
    try {
      if (editId) await API.put(`/plantillas-reporte/${editId}`, payload);
      else await API.post("/plantillas-reporte/", payload);
      setForm(INICIAL); setEditId(null); await cargar();
    } catch (error) { alert(error.response?.data?.detail || "No fue posible guardar la plantilla."); }
    finally { setGuardando(false); }
  };

  const editar = (item) => {
    setEditId(item.id); setForm({
      empresa_id: item.empresa_id || "", nombre: item.nombre, tipo: item.tipo, titulo: item.titulo,
      color_primario: item.color_primario, pie_pagina: item.pie_pagina || "", incluir_logo: item.incluir_logo,
      incluir_evidencias: item.incluir_evidencias, incluir_firmas: item.incluir_firmas,
      incluir_costos: item.incluir_costos, activo: item.activo,
    }); window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminar = async (item) => {
    if (!confirm(`¿Eliminar la plantilla "${item.nombre}"?`)) return;
    await API.delete(`/plantillas-reporte/${item.id}`); await cargar();
  };

  return (
    <AdminLayout><section className="templates-page">
      <header className="templates-hero"><div><span>DOCUMENTOS AUTOMÁTICOS</span><h1>Plantillas de reportes</h1><p>Personaliza PDFs globalmente o por empresa cliente.</p></div><FileCog size={42} /></header>
      <div className="templates-grid">
        <form className="templates-card templates-form" onSubmit={guardar}>
          <h2>{editId ? "Editar plantilla" : "Nueva plantilla"}</h2>
          <label>Alcance<select value={form.empresa_id} onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}><option value="">Global · todas las empresas</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
          <div className="templates-row"><label>Nombre<input required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></label><label>Tipo<select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}><option>AMBOS</option><option>OT</option><option>MENSUAL</option></select></label></div>
          <label>Título del documento<input required value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} /></label>
          <label>Color corporativo<input type="color" value={form.color_primario} onChange={(e) => setForm({ ...form, color_primario: e.target.value.toUpperCase() })} /></label>
          <label>Pie de página<textarea maxLength={1000} value={form.pie_pagina} onChange={(e) => setForm({ ...form, pie_pagina: e.target.value })} /></label>
          <div className="templates-checks">{[["incluir_logo", "Logo"], ["incluir_evidencias", "Evidencias"], ["incluir_firmas", "Firmas"], ["incluir_costos", "Costos"], ["activo", "Activa"]].map(([campo, label]) => <label key={campo}><input type="checkbox" checked={form[campo]} onChange={(e) => setForm({ ...form, [campo]: e.target.checked })} /> {label}</label>)}</div>
          <div className="templates-actions"><button disabled={guardando}><Plus size={16} /> {guardando ? "Guardando…" : editId ? "Actualizar" : "Crear plantilla"}</button>{editId && <button type="button" className="secondary" onClick={() => { setEditId(null); setForm(INICIAL); }}>Cancelar</button>}</div>
        </form>
        <section className="templates-card"><h2>Plantillas configuradas</h2><div className="templates-list">{items.map((item) => <article key={item.id} style={{ borderColor: item.color_primario }}><div><strong>{item.nombre}</strong><p>{item.empresa_nombre} · {item.tipo}</p><small>{item.titulo}</small></div><span className={item.activo ? "active" : "inactive"}>{item.activo ? "ACTIVA" : "INACTIVA"}</span><div className="templates-item-actions"><button onClick={() => editar(item)}><Pencil size={15} /></button><button className="danger" onClick={() => eliminar(item)}><Trash2 size={15} /></button></div></article>)}</div></section>
      </div>
    </section></AdminLayout>
  );
}
