import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import ErrorMessage from "../components/ErrorMessage";
import { getApiError } from "../api/axios";
import { useAuth } from "../context/AuthContext";
import { getDashboardEntryRoute } from "../dashboardRouting";

export default function Login() {
  const { login, loading, isAuthenticated, currentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && isAuthenticated) {
      const target = getDashboardEntryRoute(currentUser);
      navigate(target, { replace: true });
    }
  }, [loading, isAuthenticated, currentUser, navigate]);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const user = await login(form.email, form.password);
      const target = location.state?.from?.pathname || getDashboardEntryRoute(user);
      navigate(target, { replace: true });
    } catch (err) {
      const message = getApiError(err);
      setError(message);
      console.warn("Login failed:", message, err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <div className="auth-page">
        <form className="auth-card" onSubmit={submit}>
          <p className="eyebrow">Welcome back</p>
          <h1>Log in to KaziLink</h1>
          <p className="muted">Manage your services, bookings and home help in one place.</p>
          <ErrorMessage message={error} />
          <label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password<input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="green-button full" disabled={busy}>{busy ? "Logging in..." : "Log in"}</button>
          <p className="auth-switch">Don't have an account? <Link to="/register" state={{ from: location.state?.from }}>{"Create one"}</Link></p>
        </form>
      </div>
    </>
  );
}
