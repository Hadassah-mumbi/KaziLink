import { Link, useNavigate } from "react-router-dom";
import { LogIn, Menu, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getDashboardRouteForUser } from "../dashboardRouting";

export default function Navbar() {
  const { currentUser, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const dashboardPath = currentUser?.is_admin
    ? "/admin/dashboard"
    : currentUser?.is_provider
      ? "/dashboard/choose"
      : "/dashboard";

  return (
    <header className="navbar">
      <div className="nav-inner">
        <Link to="/" className="brand" onClick={() => setOpen(false)}>
          <span className="brand-mark">↗</span>
          <span>KaziLink</span>
        </Link>

        <button className="mobile-menu" onClick={() => setOpen(!open)} aria-label="Menu">
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>

        <nav className={`nav-links ${open ? "open" : ""}`}>
          <Link to="/categories" onClick={() => setOpen(false)}>Our Services</Link>

          {isAuthenticated ? (
            <>
              <Link to={dashboardPath} onClick={() => setOpen(false)}>Dashboard</Link>
              <button
                className="nav-login"
                onClick={() => {
                  logout();
                  setOpen(false);
                  navigate("/");
                }}
              >
                Log out
              </button>
            </>
          ) : (
            <Link to="/login" className="nav-login" onClick={() => setOpen(false)}>
              <LogIn size={16} /> Log in / Sign up
            </Link>
          )}

          {!currentUser?.is_provider && !currentUser?.is_admin && (
            <Link to="/become-provider" className="nav-cta" onClick={() => setOpen(false)}>
              Become a Provider
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
