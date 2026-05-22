// =========================================================
// COMPONENTE: AppLoader
// Archivo: frontend/src/components/AppLoader.jsx
// Fase 32.5 - Loader global para rutas con React.lazy.
// =========================================================

function AppLoader() {
  return (
    <div className="app-loader-pro" role="status" aria-live="polite">
      <div className="app-loader-card">
        <div className="app-loader-logo">SGA</div>
        <div className="app-loader-spinner" />
        <h1>Cargando SGA</h1>
        <p>Preparando módulo solicitado...</p>
      </div>
    </div>
  );
}

export default AppLoader;
