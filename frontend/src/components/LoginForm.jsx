// src/components/LoginForm.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Importamos para la redirección

// import '../styles/LoginForm.css'; // Asegúrate de importar tus estilos

function LoginForm({ t }) { 
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(''); // Estado para mostrar errores
    
    // Hook de navegación para redirigir al usuario
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(''); // Limpiar errores anteriores
        
        // El backend espera 'username' (el email) y 'password' en un formato especial (x-www-form-urlencoded)
        // aunque usamos un objeto FormData para simularlo fácilmente.
        const formData = new URLSearchParams();
        formData.append('username', email); // FASTAPI usa 'username'
        formData.append('password', password);

        try {
            // URL de tu API de FastAPI (Asegúrate que el puerto 8000 sea el correcto)
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: {
                    // El endpoint /login de FastAPI con OAuth2PasswordRequestForm 
                    // espera Content-Type: application/x-www-form-urlencoded
                    'Content-Type': 'application/x-www-form-urlencoded', 
                },
                body: formData.toString(), // Convertimos a string para el formato esperado
            });

            if (response.ok) {
                // Login exitoso
                const data = await response.json();
                
                // 1. Opcional: Almacenar el token o ID del usuario 
                //    (ej: en localStorage o contexto de React)
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user_id', data.user_id); 
                
                // 2. Redirigir al usuario a la página de inicio conservada
                navigate('/home'); 

            } else {
                // Login fallido (401 Unauthorized, 400 Bad Request)
                const errorData = await response.json();
                setError(errorData.detail || t('login.errorGeneric'));
            }
        } catch (err) {
            // Error de conexión (servidor caído o CORS)
            console.error('Error de conexión:', err);
            setError(t('login.errorConnection'));
        }
    };

    return (
        <form onSubmit={handleSubmit} className="login-form">
            <h2>{t('login.title')}</h2>
            
            <div className="form-group">
                <label htmlFor="email">{t('login.emailLabel')}</label>
                <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t('login.emailPlaceholder')}
                    required
                    className="responsive-input"
                />
            </div>

            <div className="form-group">
                <label htmlFor="password">{t('login.passwordLabel')}</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t('login.passwordPlaceholder')}
                    required
                    className="responsive-input"
                />
            </div>
            
            {/* Mostrar el mensaje de error si existe */}
            {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

            <button type="submit" className="login-button">
                {t('login.submitButton')}
            </button>
        </form>
    );
}

export default LoginForm;