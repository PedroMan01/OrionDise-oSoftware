import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LoginForm.css';

function LoginForm({ t }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString(),
            });

            if (response.ok) {
                const data = await response.json();
                // Guardamos el token
                localStorage.setItem('access_token', data.access_token);
                
                // ---> AQUÍ OCURRE LA REDIRECCIÓN A LA PÁGINA PRINCIPAL <---
                navigate('/home'); 
            } else {
                setError("Credenciales incorrectas");
            }
        } catch (err) {
            setError("Error de conexión");
        }
    };

    return (
        <form onSubmit={handleSubmit} className="login-form">
            <h2>{t('login.title')}</h2>
            
            {/* ... (Inputs de email y password iguales que antes) ... */}
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

            {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

            <button type="submit" className="login-button">
                {t('login.submitButton')}
            </button>

            {/* --- NUEVO: Botón para ir a Registrarse --- */}
            <div style={{ marginTop: '20px', textAlign: 'center', borderTop: '1px solid #eee', paddingTop: '10px' }}>
                <p style={{ fontSize: '0.9em', marginBottom: '10px' }}>{t('login.noAccount')}</p>
                <button 
                    type="button" 
                    onClick={() => navigate('/register')} // Redirige al formulario de registro
                    className="login-button"
                    style={{ backgroundColor: '#6c757d' }} // Un color diferente (gris)
                >
                    {t('login.createAccount')}
                </button>
            </div>
        </form>
    );
}

export default LoginForm;