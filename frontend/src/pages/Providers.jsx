import { useEffect, useState, useMemo, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import ProviderCard from "../components/ProviderCard";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import { getCategories } from "../api/categories";
import { searchProviders, searchNearbyProviders } from "../api/providers";
import { getApiError } from "../api/axios";

const GEOCODE_API = "https://maps.googleapis.com/maps/api/geocode/json";

export default function Providers() {
  const inputRef = useRef(null);
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    category_id: params.get("category") || "",
    county: "",
    town: "",
    location: "",
    latitude: "",
    longitude: "",
    available: "",
  });

  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const locationIsSet = form.latitude && form.longitude;

  async function loadProviders(searchForm = form) {
    setLoading(true);
    setError("");

    try {
      if (locationIsSet && searchForm.category_id) {
        const nearbyResults = await searchNearbyProviders({
          category_id: searchForm.category_id,
          latitude: Number(searchForm.latitude),
          longitude: Number(searchForm.longitude),
        });

        setProviders(nearbyResults);
      } else {
        const results = await searchProviders(searchForm);
        setProviders(results);
      }
    } catch (e) {
      setError(getApiError(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
    loadProviders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load Google Maps JS (Places) and attach Autocomplete to the location input.
  function loadGoogleScript(key) {
    return new Promise((resolve, reject) => {
      if (!key) return reject(new Error("Missing Google Maps API key"));
      if (window.google && window.google.maps && window.google.maps.places) return resolve();
      const existing = document.querySelector(`script[data-google-maps]`);
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

  useEffect(() => {
    if (!apiKey) return; // nothing to do without a key

    let autocomplete = null;

    loadGoogleScript(apiKey)
      .then(() => {
        if (!inputRef.current) return;
        autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
          types: ["address"],
          componentRestrictions: { country: "ke" },
        });

        autocomplete.addListener("place_changed", () => {
          const place = autocomplete.getPlace();
          if (!place || !place.geometry) return;
          const latitude = place.geometry.location.lat();
          const longitude = place.geometry.location.lng();
          const countyComponent = place.address_components?.find((c) => c.types.includes("administrative_area_level_1"));
          const townComponent =
            place.address_components?.find((c) => c.types.includes("locality")) ||
            place.address_components?.find((c) => c.types.includes("administrative_area_level_2"));

          setForm((current) => ({
            ...current,
            location: place.formatted_address || current.location,
            latitude,
            longitude,
            county: countyComponent?.long_name || current.county,
            town: townComponent?.long_name || current.town,
          }));

          // after selecting a place, auto-run provider search
          setTimeout(() => loadProviders({ ...form, latitude, longitude }), 10);
        });
      })
      .catch((err) => {
        console.warn("Google Maps script load failed:", err.message);
      });

    return () => {
      if (autocomplete && autocomplete.unbindAll) autocomplete.unbindAll();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey]);

  function handleLocationChange(value) {
    setForm((current) => ({
      ...current,
      location: value,
      latitude: "",
      longitude: "",
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    setError("");
    loadProviders();
    navigate(
      `/providers?category=${encodeURIComponent(form.category_id)}&county=${encodeURIComponent(form.county)}&town=${encodeURIComponent(
        form.town
      )}`
    );
  }

  const nearbyHint = useMemo(() => {
    if (!locationIsSet) return "Optional: search by street address or drop a pin to find nearby providers.";
    return `Searching near ${form.location || `${form.town}, ${form.county}`}`;
  }, [locationIsSet, form.location, form.town, form.county]);

  return (
    <>
      <Navbar />
      <main className="content-page">
        <div className="section-heading">
          <p className="eyebrow">Find your worker</p>
          <h1>Choose a provider</h1>
          <p>Filter the available providers and see distance to make a smarter choice.</p>
        </div>

        <form className="filter-bar" onSubmit={handleSubmit}>
          <select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
            <option value="">All services</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <input placeholder="County" value={form.county} onChange={(e) => setForm({ ...form, county: e.target.value })} />
          <input placeholder="Town" value={form.town} onChange={(e) => setForm({ ...form, town: e.target.value })} />
          <div className="location-autocomplete">
            <input
              placeholder="Street address or drop pin"
              value={form.location}
              onChange={(e) => handleLocationChange(e.target.value)}
              ref={inputRef}
            />
          </div>
          <select value={form.available} onChange={(e) => setForm({ ...form, available: e.target.value })}>
            <option value="">Any availability</option>
            <option value="true">Available now</option>
            <option value="false">Unavailable</option>
          </select>
          <button className="green-button" type="submit">
            Search
          </button>
        </form>

        <p className="muted">{nearbyHint}</p>
        <ErrorMessage message={error} />
        {loading ? (
          <Loading label="Finding providers..." />
        ) : providers.length ? (
          <div className="provider-list">{providers.map((provider) => <ProviderCard key={provider.id} provider={provider} />)}</div>
        ) : (
          <div className="empty-state">
            <h3>No providers found</h3>
            <p>Try a different service or location.</p>
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
