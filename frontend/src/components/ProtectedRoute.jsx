// src/components/ProtectedRoute.jsx

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    // 1. Verificar la autenticación
    // Revisamos si existe un token guardado en el almacenamiento local.
    const isAuthenticated = localStorage.getItem('access_token'); 

    if (!isAuthenticated) {
        // 2. Si no está autenticado, redirigir a la página de login (/)
        return <Navigate to="/" replace />;
    }

    // 3. Si está autenticado, renderizar la ruta hija (OrionListener)
    // Usamos 'children' si lo pasamos directamente, o 'Outlet' si se usa en un layout.
    return children ? children : <Outlet />;
};

export default ProtectedRoute;