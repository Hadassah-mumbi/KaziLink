import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="footer">
      <div>
        <div className="brand footer-brand"><span className="brand-mark">↗</span><span>KaziLink</span></div>
        <p>Every service your home deserves.</p>
      </div>
      <div className="footer-links">
        <Link to="/categories">Our Services</Link>
        <Link to="/providers">Find a Provider</Link>
        <Link to="/become-provider">Become a Provider</Link>
      </div>
      <p className="footer-copy">© {new Date().getFullYear()} KaziLink</p>
    </footer>
  );
}
