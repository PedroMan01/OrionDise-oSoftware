// src/components/Login.jsx

import React from 'react';
import LoginForm from './LoginForm'; // Componente del formulario (Paso 2 anterior)
import LanguageSwitcher from './LanguageSwitcher'; // Componente selector (Paso siguiente)

function Login({ t, language, setLanguage }) {
    return (
        <div className="login-page-container">
            {/* El selector de idioma debe estar visible y accesible */}
            <LanguageSwitcher 
                language={language} 
                setLanguage={setLanguage} 
                t={t}
            />
            
            <LoginForm t={t} />

            {/* Opcional: información adicional o branding */}
            <p className="footer-note">
                {t('login.projectNote')} | Diseño de Software UAI 2025
            </p>
        </div>
    );
}

export default Login;