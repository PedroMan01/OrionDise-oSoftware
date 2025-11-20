import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LoginForm.css'; // Reutilizamos los estilos del login

function RegisterForm({ t }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            // Conectamos con tu endpoint de registro en FastAPI
            const response = await fetch('http://localhost:8000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                alert("Usuario creado con éxito. Ahora puedes iniciar sesión.");
                navigate('/'); // Redirigir al Login después de registrarse
            } else {
                const data = await response.json();
                setError(data.detail || "Error al registrar usuario");
            }
        } catch (err) {
            console.error(err);
            setError("Error de conexión con el servidor");
        }
    };

    return (
        <div className="login-page-container">
            <form onSubmit={handleSubmit} className="login-form">
                <h2>{t('register.title')}</h2>
                
                <div className="form-group">
                    <label>{t('login.emailLabel')}</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="nuevo@uai.cl"
                        required
                        className="responsive-input"
                    />
                </div>

                <div className="form-group">
                    <label>{t('login.passwordLabel')}</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Crea una contraseña"
                        required
                        className="responsive-input"
                    />
                </div>

                {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

                <button type="submit" className="login-button" style={{ backgroundColor: '#28a745' }}>
                    {t('register.submitButton')}
                </button>

                {/* Botón para volver al Login si ya tiene cuenta */}
                <button 
                    type="button" 
                    onClick={() => navigate('/')}
                    style={{ marginTop: '10px', background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', width: '100%' }}
                >
                    {t('register.loginLink')}
                </button>
            </form>
        </div>
    );
}

export default RegisterForm;