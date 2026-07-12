import { useEffect, useMemo, useState } from "react";
import { Ban, CheckCircle2, CircleDollarSign, FilePlus2, Plus, Receipt, Send, Trash2, WalletCards } from "lucide-react";

import API from "../../api/axios";
import AdminLayout from "./AdminLayout";
import "../../styles/facturacion.css";

const hoy = new Date().toISOString().slice(0, 10);
const finMes = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString().slice(0, 10);
const FORM_INICIAL = {
  empresa_id: "", concepto: "Servicio de mantenimiento", moneda: "COP",
  impuesto_porcentaje: "19", periodo_inicio: hoy.slice(0, 8) + "01", periodo_fin: finMes,
  fecha_emision: hoy, fecha_vencimiento: finMes, notas: "",
  detalle: [{ descripcion: "Servicio mensual de mantenimiento", cantidad: "1", valor_unitario: "0" }],
};

export default function FacturacionPage() {
  const [facturas, setFacturas] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [resumen, setResumen] = useState({});
  const [form, setForm] = useState(FORM_INICIAL);
  const [filtro, setFiltro] = useState("");
  const [guardando, setGuardando] = useState(false);

  const cargar = async () => {
    const [facturasRes, resumenRes, empresasRes] = await Promise.all([
      API.get("/facturacion/facturas"), API.get("/facturacion/resumen"), API.get("/empresas/"),
    ]);
    setFacturas(facturasRes.data || []); setResumen(resumenRes.data || {}); setEmpresas(empresasRes.data || []);
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar().catch(console.error), 0);
    return () => window.clearTimeout(timer);
  }, []);

  const totales = useMemo(() => {
    const subtotal = form.detalle.reduce((sum, item) => sum + Number(item.cantidad || 0) * Number(item.valor_unitario || 0), 0);
    const impuesto = subtotal * Number(form.impuesto_porcentaje || 0) / 100;
    return { subtotal, impuesto, total: subtotal + impuesto };
  }, [form.detalle, form.impuesto_porcentaje]);

  const actualizarLinea = (index, campo, valor) => setForm((prev) => ({
    ...prev, detalle: prev.detalle.map((item, i) => i === index ? { ...item, [campo]: valor } : item),
  }));
  const agregarLinea = () => setForm((prev) => ({ ...prev, detalle: [...prev.detalle, { descripcion: "", cantidad: "1", valor_unitario: "0" }] }));
  const quitarLinea = (index) => setForm((prev) => ({ ...prev, detalle: prev.detalle.filter((_, i) => i !== index) }));

  const crear = async (event) => {
    event.preventDefault(); setGuardando(true);
    try {
      await API.post("/facturacion/facturas", {
        ...form, impuesto_porcentaje: Number(form.impuesto_porcentaje),
        detalle: form.detalle.map((item) => ({ ...item, cantidad: Number(item.cantidad), valor_unitario: Number(item.valor_unitario) })),
      });
      setForm(FORM_INICIAL); await cargar(); alert("Factura creada como borrador.");
    } catch (error) {
      alert(error.response?.data?.detail || "No fue posible crear la factura.");
    } finally { setGuardando(false); }
  };

  const cambiarEstado = async (factura, estado) => {
    try {
      await API.patch(`/facturacion/facturas/${factura.id}/estado`, { estado }); await cargar();
    } catch (error) { alert(error.response?.data?.detail || "No fue posible actualizar la factura."); }
  };

  const visibles = filtro ? facturas.filter((f) => f.estado === filtro) : facturas;

  return (
    <AdminLayout>
      <section className="billing-page">
        <header className="billing-hero"><div><span>CONTROL FINANCIERO</span><h1>Facturación</h1><p>Emisión, vencimientos y cartera de empresas cliente.</p></div><Receipt size={42} /></header>
        <div className="billing-kpis">
          <Kpi icon={<CircleDollarSign />} label="Total facturado" value={dinero(resumen.total_facturado)} />
          <Kpi icon={<CheckCircle2 />} label="Pagado" value={dinero(resumen.total_pagado)} good />
          <Kpi icon={<WalletCards />} label="Cartera pendiente" value={dinero(resumen.cartera_pendiente)} />
          <Kpi icon={<Ban />} label="Facturas vencidas" value={resumen.facturas_vencidas || 0} danger />
        </div>

        <div className="billing-grid">
          <form className="billing-card billing-form" onSubmit={crear}>
            <h2><FilePlus2 size={20} /> Nueva factura</h2>
            <label>Empresa *<select required value={form.empresa_id} onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}><option value="">Seleccionar</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
            <label>Concepto *<input required value={form.concepto} onChange={(e) => setForm({ ...form, concepto: e.target.value })} /></label>
            <div className="billing-row"><label>Periodo inicial<input type="date" required value={form.periodo_inicio} onChange={(e) => setForm({ ...form, periodo_inicio: e.target.value })} /></label><label>Periodo final<input type="date" required value={form.periodo_fin} onChange={(e) => setForm({ ...form, periodo_fin: e.target.value })} /></label></div>
            <div className="billing-row"><label>Emisión<input type="date" required value={form.fecha_emision} onChange={(e) => setForm({ ...form, fecha_emision: e.target.value })} /></label><label>Vencimiento<input type="date" required value={form.fecha_vencimiento} onChange={(e) => setForm({ ...form, fecha_vencimiento: e.target.value })} /></label></div>
            <h3>Conceptos</h3>
            {form.detalle.map((linea, index) => <div className="billing-line" key={index}><input required placeholder="Descripción" value={linea.descripcion} onChange={(e) => actualizarLinea(index, "descripcion", e.target.value)} /><input required type="number" min="0.01" step="0.01" value={linea.cantidad} onChange={(e) => actualizarLinea(index, "cantidad", e.target.value)} /><input required type="number" min="0" step="0.01" value={linea.valor_unitario} onChange={(e) => actualizarLinea(index, "valor_unitario", e.target.value)} /><button type="button" disabled={form.detalle.length === 1} onClick={() => quitarLinea(index)}><Trash2 size={15} /></button></div>)}
            <button type="button" className="billing-add" onClick={agregarLinea}><Plus size={15} /> Agregar concepto</button>
            <label>IVA %<input type="number" min="0" max="100" step="0.01" value={form.impuesto_porcentaje} onChange={(e) => setForm({ ...form, impuesto_porcentaje: e.target.value })} /></label>
            <div className="billing-total"><span>Subtotal {dinero(totales.subtotal)}</span><span>IVA {dinero(totales.impuesto)}</span><strong>Total {dinero(totales.total)}</strong></div>
            <button className="billing-primary" disabled={guardando}><FilePlus2 size={16} /> {guardando ? "Creando…" : "Crear borrador"}</button>
          </form>

          <section className="billing-card billing-list">
            <div className="billing-list-head"><div><h2>Facturas</h2><p>{visibles.length} registros</p></div><select value={filtro} onChange={(e) => setFiltro(e.target.value)}><option value="">Todos los estados</option>{["BORRADOR", "EMITIDA", "PAGADA", "VENCIDA", "ANULADA"].map((e) => <option key={e}>{e}</option>)}</select></div>
            <div className="billing-table-wrap"><table><thead><tr><th>Número / empresa</th><th>Vencimiento</th><th>Total</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>{visibles.map((f) => <tr key={f.id}><td><strong>{f.numero}</strong><small>{f.empresa_nombre}<br />{f.concepto}</small></td><td>{f.fecha_vencimiento}</td><td>{dinero(f.total, f.moneda)}</td><td><span className={`billing-badge ${f.estado.toLowerCase()}`}>{f.estado}</span></td><td><div className="billing-actions">{f.estado_persistido === "BORRADOR" && <button onClick={() => cambiarEstado(f, "EMITIDA")}><Send size={14} /> Emitir</button>}{f.estado_persistido === "EMITIDA" && <button onClick={() => cambiarEstado(f, "PAGADA")}><CheckCircle2 size={14} /> Pagar</button>}{["BORRADOR", "EMITIDA"].includes(f.estado_persistido) && <button className="danger" onClick={() => cambiarEstado(f, "ANULADA")}><Ban size={14} /> Anular</button>}</div></td></tr>)}</tbody></table></div>
          </section>
        </div>
      </section>
    </AdminLayout>
  );
}

function Kpi({ icon, label, value, good, danger }) { return <article className={`billing-kpi ${good ? "good" : ""} ${danger ? "danger" : ""}`}><span>{icon}</span><div><small>{label}</small><strong>{value}</strong></div></article>; }
function dinero(value, moneda = "COP") { return new Intl.NumberFormat("es-CO", { style: "currency", currency: moneda || "COP", maximumFractionDigits: 0 }).format(Number(value || 0)); }
