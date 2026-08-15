import { Link } from "react-router-dom";
import { ArrowRight, Search, ShieldCheck, CalendarCheck, Smartphone } from "lucide-react";
import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import CategoryCard from "../components/CategoryCard";
import { getCategories } from "../api/categories";
import { getApiError } from "../api/axios";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function Home() {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getCategories().then(setCategories).catch((e) => setError(getApiError(e)));
  }, []);

  return (
    <>
      <Navbar />
      <main>
        <section className="hero">
          <div className="hero-image">
            <div className="hero-deco deco-one" />
            <div className="hero-deco deco-two" />
            <div className="hero-deco deco-three" />
            <div className="hero-title">Every service your home deserves</div>
          </div>

          <form className="home-search" onSubmit={(e) => {
            e.preventDefault();
            const q = new FormData(e.currentTarget).get("service");
            window.location.href = `/providers${q ? `?q=${encodeURIComponent(q)}` : ""}`;
          }}>
            <input name="service" placeholder="What service do you need?" />
            <button><Search size={16} /> Search</button>
          </form>

          <div className="home-categories">
            {categories.length ? categories.slice(0, 9).map((c) => <CategoryCard key={c.id} category={c} compact />) : <Loading label="Loading services..." />}
          </div>
          <ErrorMessage message={error} />
        </section>

        <section className="cream-section">
          <div className="section-heading center">
            <p className="eyebrow">How KaziLink works</p>
            <h2>Getting help at home, made simple.</h2>
            <p>Find the service you need, choose a provider and manage your booking from one place.</p>
          </div>
          <div className="feature-grid">
            <div className="feature-card"><CalendarCheck /><h3>Bookings</h3><p>Choose a service, date and time that works for you.</p></div>
            <div className="feature-card"><ShieldCheck /><h3>Trusted providers</h3><p>Provider applications go through the KaziLink approval process.</p></div>
            <div className="feature-card"><Smartphone /><h3>Easy management</h3><p>Keep track of your bookings, reviews and provider activity.</p></div>
          </div>
        </section>

        <section className="simple-section split-section">
          <div>
            <p className="eyebrow">Find the help you need</p>
            <h2>Home services without the hassle.</h2>
            <p>Search by service, location, availability and experience, then view a provider profile before you book.</p>
            <Link to="/providers" className="green-button">Find a provider <ArrowRight size={17} /></Link>
          </div>
          <div className="phone-art">
            <div className="phone-screen"><div className="phone-top">KaziLink</div><div className="phone-card">Your booking is confirmed ✓</div><div className="phone-card">Provider: Your chosen professional</div></div>
          </div>
        </section>

        <section className="cream-section">
          <div className="section-heading center">
            <p className="eyebrow">For providers</p>
            <h2>Bring your services to KaziLink.</h2>
            <p>Create a provider profile, set your services and availability, and manage incoming bookings.</p>
            <Link to="/become-provider" className="outline-button">Become a Provider</Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
