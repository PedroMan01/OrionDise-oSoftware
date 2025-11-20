// src/i18n/i18n.js
import es from './es.json'; // ⬅️ 1. Importa los archivos JSON de idiomas
import en from './en.json';

const translations = { es, en };

// La función 'translate' que busca la clave en el idioma seleccionado
export const translate = (lang, key) => { 
    const keys = key.split('.');
    let result = translations[lang];

    for (const k of keys) {
        if (!result || !result[k]) {
            return key; // Si no la encuentra, retorna la clave original
        }
        result = result[k];
    }
    return result;
};