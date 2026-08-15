import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import ErrorMessage from "../components/ErrorMessage";
import { getApiError } from "../api/axios";
import { registerCustomer } from "../api/auth";

export default function Register() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", phone: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await registerCustomer(form);
      navigate("/login", { state: { message: "Account created. Please log in.", from: location.state?.from } });
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <div className="auth-page">
        <form className="auth-card" onSubmit={submit}>
          <p className="eyebrow">Join KaziLink</p>
          <h1>Create your account</h1>
          <ErrorMessage message={error} />
          <div className="form-grid two">
            <label>First name<input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></label>
            <label>Last name<input required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></label>
          </div>
          <label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Phone<input required value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
          <label>Password<input type="password" minLength="8" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="green-button full" disabled={busy}>{busy ? "Creating account..." : "Create account"}</button>
          <p className="auth-switch">Already have an account? <Link to="/login" state={location.state}>Log in</Link></p>
        </form>
      </div>
    </>
  );
}
