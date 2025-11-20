import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";
// Componentes del proyecto anterior (mantenemos solo OrionListener)
import OrionListener from "./components/OrionListener";

// NUEVO: Componente Login que incluye el formulario y el selector de idioma
import Login from "./components/Login";
import ProtectedRoute from "./components/ProtectedRoute"; // NUEVO: Importamos el componente protector

// NUEVO: Importar los archivos de idioma y la función de traducción
import es from './i18n/es.json';
import en from './i18n/en.json'; // Asumiendo el segundo idioma es inglés

// Función de traducción simple dentro de App.jsx (para simplicidad)
const translations = { es, en };

const translate = (lang, key) => {
    const keys = key.split('.');
    let result = translations[lang];

    for (const k of keys) {
        if (!result || !result[k]) {
            return key; 
        }
        result = result[k];
    }
    return result;
};


function App() {
    // Estado para manejar el idioma actual (default: español)
    const [language, setLanguage] = useState('es');
    
    // La función 't' que se pasa a los componentes para traducir
    const t = (key) => translate(language, key);

    return (
        <>
            <Routes>
                {/* 1. Ruta de Login (Pública) */}
                <Route 
                    path="/" 
                    element={
                        <Login 
                            t={t}
                            language={language}
                            setLanguage={setLanguage}
                        />
                    } 
                />

                {/* 2. Ruta Protegida: Solo accesible con Token */}
                <Route 
                    path="/home" 
                    element={
                        <ProtectedRoute>
                            {/* Este componente solo se renderiza si hay un token válido */}
                            <OrionListener />
                        </ProtectedRoute>
                    } 
                />
            </Routes>
        </>
    );
}

export default App;