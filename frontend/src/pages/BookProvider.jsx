import { useEffect, useState, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import ErrorMessage from "../components/ErrorMessage";
import Loading from "../components/Loading";
import { getProvider } from "../api/providers";
import { getCategories } from "../api/categories";
import { createBooking } from "../api/bookings";
import { getApiError } from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function BookProvider() {
  const { providerId } = useParams();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [provider, setProvider] = useState(null);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    category_id: "",
    booking_date: "",
    booking_time: "",
    county: "",
    town: "",
    address: "",
    latitude: "",
    longitude: "",
    description: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const addressRef = useRef(null);
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

  useEffect(() => {
    Promise.all([getProvider(providerId), getCategories()])
      .then(([p, c]) => {
        setProvider(p);
        setCategories(c);
        if (p.services?.length) setForm((old) => ({ ...old, category_id: p.services[0].category_id }));
        setForm((old) => ({ ...old, county: p.county, town: p.town }));
      })
      .catch((e) => setError(getApiError(e)));
  }, [providerId]);

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

  function handleAddressChange(value) {
    setForm((current) => ({
      ...current,
      address: value,
      latitude: "",
      longitude: "",
    }));
  }

  async function submit(e) {
    e.preventDefault();
    if (!isAuthenticated) { navigate("/login"); return; }
    setError(""); setBusy(true);
    try {
      const data = await createBooking({ provider_id: providerId, ...form });
      navigate(`/dashboard/bookings/${data.booking.id}`);
    } catch (e) {
      setError(getApiError(e));
    } finally { setBusy(false); }
  }

  if (!provider && !error) return <><Navbar /><Loading label="Loading booking form..." /></>;

  const offered = categories.filter((c) => provider?.services?.some((s) => s.category_id === c.id));

  return (
    <>
      <Navbar />
      <main className="content-page booking-flow">
        <div className="booking-progress"><span className="active">1 Service</span><span>2 Details</span><span>3 Confirm</span></div>
        <div className="section-heading">
          <p className="eyebrow">Book your provider</p>
          <h1>Tell us what you need.</h1>
          <p>We will send the booking request to your chosen provider.</p>
        </div>

        <form className="booking-form panel" onSubmit={submit}>
          <ErrorMessage message={error} />
          <label>Service
            <select required value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
              <option value="">Choose a service</option>
              {offered.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </label>

          <div className="form-grid two">
            <label>Date<input type="date" required value={form.booking_date} onChange={(e) => setForm({ ...form, booking_date: e.target.value })} /></label>
            <label>Start time<input type="time" required value={form.booking_time} onChange={(e) => setForm({ ...form, booking_time: e.target.value })} /></label>
          </div>

          <div className="form-grid two">
            <label>County<input required value={form.county} onChange={(e) => setForm({ ...form, county: e.target.value })} /></label>
            <label>Town<input required value={form.town} onChange={(e) => setForm({ ...form, town: e.target.value })} /></label>
          </div>

          <label>Street address<input placeholder="E.g. 98 Oxford Street" value={form.address} onChange={(e) => handleAddressChange(e.target.value)} ref={addressRef} /></label>
          <label>Anything else we should know?<textarea rows="5" placeholder="Tell your provider about the job..." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>

          <div className="booking-summary">
            <div><span>Provider</span><strong>{provider?.town}, {provider?.county}</strong></div>
            <div><span>Hourly rate</span><strong>KSh {Number(provider?.hourly_rate || 0).toLocaleString()}</strong></div>
          </div>

          <button className="green-button full" disabled={busy}>{busy ? "Creating booking..." : "Request booking"}</button>
        </form>
      </main>
    </>
  );
}
