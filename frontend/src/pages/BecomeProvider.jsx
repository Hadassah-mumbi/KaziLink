import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import ErrorMessage from "../components/ErrorMessage";
import { applyAsProvider } from "../api/providers";
import { getApiError } from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function BecomeProvider() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, currentUser } = useAuth();
  const addressRef = useRef(null);
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const [form, setForm] = useState({ bio: "", address: "", county: "", town: "", latitude: "", longitude: "", experience_years: 0, hourly_rate: "", daily_rate: "" });
  const [documents, setDocuments] = useState({ nationalId: null, goodConduct: null });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (isAuthenticated && currentUser?.is_provider) {
      navigate("/provider/dashboard", { replace: true });
    }
  }, [isAuthenticated, currentUser, navigate]);

  useEffect(() => {
    if (!apiKey || !addressRef.current) return;

    function loadGoogleScript(key) {
      return new Promise((resolve, reject) => {
        if (window.google?.maps?.places) return resolve();
        const existing = document.querySelector("script[data-google-maps]");
        if (existing) {
          existing.addEventListener("load", () => resolve());
          existing.addEventListener("error", () => reject(new Error("Google Maps failed to load")));
          return;
        }

        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=places&v=weekly`;
        script.async = true;
        script.defer = true;
        script.setAttribute("data-google-maps", "loaded");
        script.onload = () => resolve();
        script.onerror = () => reject(new Error("Google Maps failed to load"));
        document.head.appendChild(script);
      });
    }

    let autocomplete = null;

    loadGoogleScript(apiKey)
      .then(() => {
        if (!addressRef.current) return;

        autocomplete = new window.google.maps.places.Autocomplete(addressRef.current, {
          types: ["address"],
          componentRestrictions: { country: "ke" },
        });

        autocomplete.addListener("place_changed", () => {
          const place = autocomplete.getPlace();
          if (!place || !place.geometry) return;

          const addressComponents = place.address_components || [];
          const countyComponent = addressComponents.find((c) => c.types.includes("administrative_area_level_1"));
          const townComponent =
            addressComponents.find((c) => c.types.includes("locality")) ||
            addressComponents.find((c) => c.types.includes("administrative_area_level_2"));

          setForm((current) => ({
            ...current,
            address: place.formatted_address || current.address,
            latitude: place.geometry.location.lat(),
            longitude: place.geometry.location.lng(),
            county: countyComponent?.long_name || current.county,
            town: townComponent?.long_name || current.town,
          }));
        });
      })
      .catch((err) => {
        console.warn("Google Maps autocomplete failed:", err.message);
      });

    return () => {
      if (autocomplete?.unbindAll) autocomplete.unbindAll();
    };
  }, [apiKey]);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);

    if (!isAuthenticated) {
      navigate("/login", { state: { from: location } });
      setBusy(false);
      return;
    }

    if (!form.latitude || !form.longitude) {
      setError("Please select your address from the autocomplete suggestions so we can capture your location.");
      setBusy(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("bio", form.bio);
      formData.append("county", form.county);
      formData.append("town", form.town);
      formData.append("latitude", String(form.latitude));
      formData.append("longitude", String(form.longitude));
      formData.append("experience_years", String(form.experience_years));
      formData.append("hourly_rate", String(form.hourly_rate));
      formData.append("daily_rate", String(form.daily_rate));

      if (documents.nationalId) {
        formData.append("national_id_document", documents.nationalId);
      }

      if (documents.goodConduct) {
        formData.append("good_conduct_certificate", documents.goodConduct);
      }

      await applyAsProvider(formData);
      navigate("/provider/dashboard");
    } catch (e) {
      setError(getApiError(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="content-page narrow">
        <div className="section-heading"><p className="eyebrow">Become a provider</p><h1>Tell us about your services.</h1><p>Your application will be reviewed before your provider profile is visible to customers.</p></div>
        <form className="panel form-stack" onSubmit={submit}>
          <ErrorMessage message={error} />
          {!isAuthenticated && (
            <div className="info-banner">
              <p>
                You need an account to apply as a provider. <strong>Please log in or register</strong> before submitting your application.
              </p>
              <p>
                <Link to="/login">Log in</Link> or <Link to="/register">Create an account</Link>.
              </p>
            </div>
          )}
          <label>About you<textarea required minLength="20" rows="6" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} /></label>
          <label>Street address<input
            placeholder="E.g. 98 Oxford Street, Nairobi"
            ref={addressRef}
            required
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
          /></label>
          <div className="form-grid two">
            <label>County<input required value={form.county} onChange={(e) => setForm({ ...form, county: e.target.value })} /></label>
            <label>Town<input required value={form.town} onChange={(e) => setForm({ ...form, town: e.target.value })} /></label>
          </div>
          <div className="form-grid three">
            <label>Experience (years)<input type="number" min="0" max="60" required value={form.experience_years} onChange={(e) => setForm({ ...form, experience_years: e.target.value })} /></label>
            <label>Hourly rate<input type="number" min="1" required value={form.hourly_rate} onChange={(e) => setForm({ ...form, hourly_rate: e.target.value })} /></label>
            <label>Daily rate<input type="number" min="1" required value={form.daily_rate} onChange={(e) => setForm({ ...form, daily_rate: e.target.value })} /></label>
          </div>
          <div className="form-grid two">
            <label>National ID document<input type="file" accept=".pdf,.jpg,.jpeg,.png" required onChange={(e) => setDocuments({ ...documents, nationalId: e.target.files?.[0] || null })} /></label>
            <label>Good conduct certificate<input type="file" accept=".pdf,.jpg,.jpeg,.png" required onChange={(e) => setDocuments({ ...documents, goodConduct: e.target.files?.[0] || null })} /></label>
          </div>
          <button className="green-button full" disabled={busy}>{busy ? "Submitting..." : "Submit provider application"}</button>
        </form>
      </main>
    </>
  );
}
