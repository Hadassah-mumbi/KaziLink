import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";
import { setDashboardSelection } from "../dashboardRouting";

export default function DashboardChooser() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const chooseDashboard = (mode) => {
    if (!currentUser?.is_provider) {
      navigate("/dashboard", { replace: true });
      return;
    }

    setDashboardSelection(mode);
    navigate(mode === "provider" ? "/provider/dashboard" : "/dashboard", { replace: true });
  };

  return (
    <>
      <Navbar />
      <main className="content-page narrow">
        <div className="section-heading center">
          <p className="eyebrow">Choose your dashboard</p>
          <h1>Welcome back, {currentUser?.first_name || "there"}</h1>
          <p>You are both a customer and a provider on KaziLink. Pick the dashboard you want to open now.</p>
        </div>

        <div className="two-column" style={{ maxWidth: 760, margin: "0 auto" }}>
          <button className="panel" style={{ textAlign: "left", border: "1px solid #dfe9e0", background: "#fff" }} onClick={() => chooseDashboard("customer")}>
            <p className="eyebrow">Customer</p>
            <h2 style={{ margin: "8px 0 6px" }}>Customer dashboard</h2>
            <p style={{ margin: 0 }}>Manage bookings, reviews, and your home service requests.</p>
          </button>

          <button className="panel" style={{ textAlign: "left", border: "1px solid #dfe9e0", background: "#fff" }} onClick={() => chooseDashboard("provider")}>
            <p className="eyebrow">Provider</p>
            <h2 style={{ margin: "8px 0 6px" }}>Provider dashboard</h2>
            <p style={{ margin: 0 }}>Track incoming bookings, update services, and manage availability.</p>
          </button>
        </div>
      </main>
    </>
  );
}
