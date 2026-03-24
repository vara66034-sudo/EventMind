import { Navigate } from 'react-router-dom';
import { authAPI } from '../api/auth';

const ProtectedRoute = ({ children }) => {
    if (!authAPI.isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }
    return children;
};

export default ProtectedRoute;
