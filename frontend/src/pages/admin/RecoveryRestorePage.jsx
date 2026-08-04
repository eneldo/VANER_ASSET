// ============================================================
// RECOVERY & RESTORE PRO
// ============================================================

import { useEffect, useState } from "react";

import axios from "../../api/axios";

import AdminLayout from "./AdminLayout";

import "../../styles/recovery-restore.css";

export default function RecoveryRestorePage() {

  const [backups, setBackups] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  // ============================================================
  // CARGAR
  // ============================================================

  const cargarDatos = async () => {

    try {

      const backupsRes = await axios.get("/recovery/backups");

      const statusRes = await axios.get("/recovery/status");

      setBackups(backupsRes.data);

      setStatus(statusRes.data);

    } catch (error) {

      console.error(error);

    }

  };

  // ============================================================
  // CREAR BACKUP
  // ============================================================

  const crearBackup = async () => {

    try {

      setLoading(true);

      await axios.post("/recovery/backup");

      await cargarDatos();

      alert("Backup generado correctamente");

    } catch (error) {

      console.error(error);

      alert("Error generando backup");

    } finally {

      setLoading(false);

    }

  };

  // ============================================================
  // RESTAURAR
  // ============================================================

  const restaurarBackup = async (archivo) => {

    const confirmar = window.confirm(
      `¿Deseas restaurar el backup ${archivo}?`
    );

    if (!confirmar) return;

    const confirmacion = window.prompt(
      'Escribe RESTAURAR_BASE_DE_DATOS para continuar'
    );

    if (confirmacion !== 'RESTAURAR_BASE_DE_DATOS') return;

    try {

      await axios.post("/recovery/restore", {
        archivo_backup: archivo,
        confirmacion
      });

      alert("Sistema restaurado correctamente");

    } catch (error) {

      console.error(error);

      alert("Error restaurando backup");

    }

  };

  // ============================================================
  // INIT
  // ============================================================

  useEffect(() => {

    const timer = window.setTimeout(() => cargarDatos(), 0);
    return () => window.clearTimeout(timer);

  }, []);

  return (

    <AdminLayout>

      <div className="recovery-page">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="recovery-header">

          <div>

            <span className="recovery-badge">
              RECOVERY & RESTORE PRO
            </span>

            <h1>
              Centro de Backups Inteligentes
            </h1>

            <p>
              Gestión profesional de respaldos,
              recuperación y restauración segura
              PostgreSQL SaaS Enterprise.
            </p>

          </div>

          <button
            className="btn-backup"
            onClick={crearBackup}
            disabled={loading}
          >
            {loading
              ? "Generando..."
              : "Crear Backup"}
          </button>

        </div>

        {/* ================================================= */}
        {/* STATS */}
        {/* ================================================= */}

        {status && (

          <div className="status-grid">

            <div className="status-card">

              <h3>PostgreSQL</h3>

              <span>
                {status.postgres
                  ? "ONLINE"
                  : "OFFLINE"}
              </span>

            </div>

            <div className="status-card">

              <h3>Total Backups</h3>

              <span>
                {status.backups_totales}
              </span>

            </div>

            <div className="status-card">

              <h3>Último Backup</h3>

              <span>
                {status.ultimo_backup || "N/A"}
              </span>

            </div>

          </div>

        )}

        {/* ================================================= */}
        {/* TABLA */}
        {/* ================================================= */}

        <div className="table-container">

          <table className="recovery-table">

            <thead>

              <tr>
                <th>Archivo</th>
                <th>Tamaño</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>

            </thead>

            <tbody>

              {backups.length === 0 ? (

                <tr>

                  <td
                    colSpan="4"
                    className="empty-row"
                  >
                    No existen backups generados
                  </td>

                </tr>

              ) : (

                backups.map((backup, index) => (

                  <tr key={index}>

                    <td>{backup.nombre}</td>

                    <td>
                      {backup.tamaño_mb} MB
                    </td>

                    <td>
                      {new Date(
                        backup.fecha
                      ).toLocaleString()}
                    </td>

                    <td className="actions">

                      <a
                        href={`${import.meta.env.VITE_API_URL}/recovery/download/${backup.nombre}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn-download"
                      >
                        Descargar
                      </a>

                      <button
                        className="btn-restore"
                        onClick={() =>
                          restaurarBackup(
                            backup.nombre
                          )
                        }
                      >
                        Restaurar
                      </button>

                    </td>

                  </tr>

                ))

              )}

            </tbody>

          </table>

        </div>

      </div>

    </AdminLayout>

  );
}
