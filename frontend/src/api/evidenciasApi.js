/*
===========================================================
API SEGURA EVIDENCIAS
===========================================================
*/

import axios from "axios";

const API = "http://127.0.0.1:8000/evidencias";

export const subirEvidencia = async (formData) => {

    const token = localStorage.getItem("token");

    return axios.post(
        `${API}/subir`,
        formData,
        {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "multipart/form-data"
            }
        }
    );
};