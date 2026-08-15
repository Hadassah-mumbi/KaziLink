import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Sidebar from "./Sidebar";

export default function DashboardShell({ type, title, subtitle, children, actions }) {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const canSwitchDashboard = currentUser?.is_provider && !currentUser?.is_admin;

  return (
    <div className="dashboard-layout">
      <Sidebar type={type} />
      <main className="dashboard-main">
        <div className="dashboard-heading">
          <div>
            <p className="eyebrow">{type === "admin" ? "KaziLink administration" : type === "provider" ? "Provider space" : "Customer space"}</p>
            <h1>{title}</h1>
            {subtitle && <p className="muted">{subtitle}</p>}
          </div>
          <div className="dashboard-heading-actions">
            {actions}
            {canSwitchDashboard && (
              <button type="button" className="outline-button small" onClick={() => navigate("/dashboard/choose", { replace: false })}>
                Switch dashboard
              </button>
            )}
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}
