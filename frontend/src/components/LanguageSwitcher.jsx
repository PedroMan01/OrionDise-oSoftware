// src/components/LanguageSwitcher.jsx

import React from 'react';
import '../styles/LanguageSwitcher.css';

function LanguageSwitcher({ language, setLanguage }) {
    
    // Función para cambiar el idioma
    const toggleLanguage = (newLang) => {
        setLanguage(newLang);
    };

    return (
        <div className="language-switcher">
            <button 
                onClick={() => toggleLanguage('es')} 
                className={language === 'es' ? 'active' : ''}
            >
                ES
            </button>
            {' | '}
            <button 
                onClick={() => toggleLanguage('en')} 
                className={language === 'en' ? 'active' : ''}
            >
                EN
            </button>
        </div>
    );
}

export default LanguageSwitcher;