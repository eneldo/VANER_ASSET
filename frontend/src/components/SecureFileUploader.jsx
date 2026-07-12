/*
===========================================================
UPLOADER SEGURO PRO
===========================================================
*/

import { useState } from "react";

import { subirEvidencia } from "../api/evidenciasApi";

import "../styles/evidencias-security.css";

const MAX_SIZE = 15 * 1024 * 1024;

export default function SecureFileUploader() {

    const [file, setFile] = useState(null);

    const allowed = [
        "image/jpeg",
        "image/png",
        "application/pdf"
    ];

    const handleFile = (e) => {

        const selected = e.target.files[0];

        if (!selected) return;

        // ==============================================
        // VALIDAR MIME
        // ==============================================

        if (!allowed.includes(selected.type)) {

            alert("Archivo no permitido");

            return;
        }

        // ==============================================
        // VALIDAR TAMAÑO
        // ==============================================

        if (selected.size > MAX_SIZE) {

            alert("Archivo supera 15MB");

            return;
        }

        setFile(selected);
    };

    const handleUpload = async () => {

        if (!file) {
            alert("Seleccione archivo");
            return;
        }

        const formData = new FormData();

        formData.append("archivo", file);
        formData.append("mantenimiento_id", "demo");
        formData.append("tipo", "ANTES");

        try {

            await subirEvidencia(formData);

            alert("Archivo subido correctamente");

        } catch (error) {

            console.error(error);

            alert("Error al subir");
        }
    };

    return (
        <div className="secure-upload-box">

            <h3>Subida Segura PRO</h3>

            <input
                type="file"
                onChange={handleFile}
            />

            {
                file && (
                    <div className="file-preview">

                        <p>{file.name}</p>

                        <p>
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>

                    </div>
                )
            }

            <button onClick={handleUpload}>
                Subir Evidencia
            </button>

        </div>
    );
}
