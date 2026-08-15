import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getStoredDashboardSelection } from "../dashboardRouting";

export default function ProtectedRoute({ role }) {
  const { loading, isAuthenticated, currentUser } = useAuth();
  const location = useLocation();

  if (loading) return <div className="page-center">Loading KaziLink...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location }} />;

  if (role === "admin" && !currentUser?.is_admin) return <Navigate to="/dashboard" replace />;
  if (role === "provider" && !currentUser?.is_provider) return <Navigate to="/dashboard" replace />;

  if (role === "customer" && currentUser?.is_admin) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return <Outlet />;
}
