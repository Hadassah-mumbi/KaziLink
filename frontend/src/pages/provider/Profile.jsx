import { useEffect, useRef, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import ErrorMessage from "../../components/ErrorMessage";
import Loading from "../../components/Loading";
import { getMyProvider, updateProviderLocation, updateServiceRadius, updateProviderProfile } from "../../api/providers";
import { getApiError } from "../../api/axios";
import { useAuth } from "../../context/AuthContext";

export default function ProviderProfile() {
  const { refreshUser } = useAuth();
  const locationSearchRef = useRef(null);
  const autocompleteRef = useRef(null);
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const [provider, setProvider] = useState(null);
  const [location, setLocation] = useState({ latitude: "", longitude: "" });
  const [locationSearch, setLocationSearch] = useState("");
  const [radius, setRadius] = useState("");
  const [form, setForm] = useState({ bio: "", county: "", town: "", experience_years: "", hourly_rate: "", daily_rate: "" });
  const [photoFile, setPhotoFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getMyProvider()
      .then((p) => {
        setProvider(p);
        setLocation({ latitude: p.latitude ?? "", longitude: p.longitude ?? "" });
        setLocationSearch(p.town || "");
        setRadius(p.service_radius_km ?? "");
        setForm({
          bio: p.bio ?? "",
          county: p.county ?? "",
          town: p.town ?? "",
          experience_years: p.experience_years ?? "",
          hourly_rate: p.hourly_rate ?? "",
          daily_rate: p.daily_rate ?? "",
        });
        setPreview(p.profile_picture ?? "");
      })
      .catch((e) => setError(getApiError(e)));
  }, []);

  useEffect(() => {
    if (!apiKey) return;

    let autocomplete = null;

    const loadGoogleScript = (key) => new Promise((resolve, reject) => {
      if (window.google?.maps?.places) return resolve();

      const existing = document.querySelector("script[data-google-maps]");
      if (existing) {
        if (window.google?.maps?.places || existing.readyState === "loaded" || existing.readyState === "complete") {
          return resolve();
        }
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

    const initAutocomplete = () => {
      if (!locationSearchRef.current || !window.google?.maps?.places || autocompleteRef.current) return;

      autocomplete = new window.google.maps.places.Autocomplete(locationSearchRef.current, {
        fields: ["geometry", "formatted_address", "address_components"],
        types: ["address"],
        componentRestrictions: { country: "ke" },
      });
      autocompleteRef.current = autocomplete;

      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place || !place.geometry) return;

        const addressComponents = place.address_components || [];
        const countyComponent = addressComponents.find((c) => c.types.includes("administrative_area_level_1"));
        const townComponent =
          addressComponents.find((c) => c.types.includes("locality")) ||
          addressComponents.find((c) => c.types.includes("administrative_area_level_2"));

        setLocationSearch(place.formatted_address || place.name || "");
        setLocation((current) => ({
          ...current,
          latitude: place.geometry.location.lat(),
          longitude: place.geometry.location.lng(),
        }));
        setForm((current) => ({
          ...current,
          county: countyComponent?.long_name || current.county,
          town: townComponent?.long_name || current.town,
        }));
      });
    };

    loadGoogleScript(apiKey)
      .then(initAutocomplete)
      .catch((err) => {
        console.warn("Google Maps autocomplete failed:", err.message);
      });

    return () => {
      if (autocomplete?.unbindAll) autocomplete.unbindAll();
    };
  }, [apiKey, provider]);

  function handleLocationSearchChange(value) {
    setLocationSearch(value);
    setLocation((current) => ({ ...current, latitude: "", longitude: "" }));
    if (autocompleteRef.current && locationSearchRef.current) {
      // trigger autocomplete suggestions after user types
      locationSearchRef.current.focus();
    }
  }

  async function saveProfile(e) {
    e.preventDefault();
    setError("");
    setMessage("");

    try {
      const payload = {
        bio: form.bio,
        county: form.county,
        town: form.town,
        profile_picture: photoFile,
      };

      if (form.experience_years !== "") {
        payload.experience_years = Number(form.experience_years);
      }
      if (form.hourly_rate !== "") {
        payload.hourly_rate = Number(form.hourly_rate);
      }
      if (form.daily_rate !== "") {
        payload.daily_rate = Number(form.daily_rate);
      }

      const p = await updateProviderProfile(payload);

      setProvider(p);
      setPreview(p.profile_picture ?? preview);
      setMessage("Profile updated.");
      // Refresh the user context to update profile picture across all pages
      await refreshUser();
    } catch (e) {
      setError(getApiError(e));
    }
  }

  async function saveLocation(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      const p = await updateProviderLocation({ latitude: Number(location.latitude), longitude: Number(location.longitude) });
      setProvider(p);
      setMessage("Location updated.");
    } catch (e) {
      setError(getApiError(e));
    }
  }

  async function saveRadius(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      const p = await updateServiceRadius({ service_radius_km: Number(radius) });
      setProvider(p);
      setMessage("Service radius updated.");
    } catch (e) {
      setError(getApiError(e));
    }
  }

  if (!provider && !error) return <DashboardShell type="provider" title="My profile"><Loading /></DashboardShell>;

  return (
    <DashboardShell type="provider" title="My provider profile" subtitle="Your backend currently supports location and service-radius updates from this screen.">
      <ErrorMessage message={error || message} />
      {provider && <div className="profile-grid">
        <section className="panel">
          <h2>Profile</h2>
          <div className="profile-image-edit">
            <div className="large-avatar">
              {preview ? <img src={preview} alt={provider.bio || "Provider"} /> : (provider.bio?.charAt(0).toUpperCase() || "P")}
            </div>
            <div>
              <p>{provider.bio}</p>
              <div className="details-grid">
                <div><span>County</span><strong>{provider.county}</strong></div>
                <div><span>Town</span><strong>{provider.town}</strong></div>
                <div><span>Experience</span><strong>{provider.experience_years} years</strong></div>
                <div><span>Hourly rate</span><strong>KSh {Number(provider.hourly_rate).toLocaleString()}</strong></div>
                <div><span>Daily rate</span><strong>KSh {Number(provider.daily_rate).toLocaleString()}</strong></div>
                <div><span>Approval</span><strong>{provider.approved ? "Approved" : "Pending"}</strong></div>
              </div>
            </div>
          </div>
        </section>
        <section className="panel form-stack">
          <h2>Edit profile</h2>
          <form onSubmit={saveProfile} encType="multipart/form-data">
            <label>Bio<textarea required value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} /></label>
            <label>County<input type="text" required value={form.county} onChange={(e) => setForm({ ...form, county: e.target.value })} /></label>
            <label>Town<input type="text" required value={form.town} onChange={(e) => setForm({ ...form, town: e.target.value })} /></label>
            <label>Experience years<input type="number" min="0" value={form.experience_years} onChange={(e) => setForm({ ...form, experience_years: e.target.value })} /></label>
            <label>Hourly rate<input type="number" min="0" step="0.01" value={form.hourly_rate} onChange={(e) => setForm({ ...form, hourly_rate: e.target.value })} /></label>
            <label>Daily rate<input type="number" min="0" step="0.01" value={form.daily_rate} onChange={(e) => setForm({ ...form, daily_rate: e.target.value })} /></label>
            <label>Profile picture<input type="file" accept="image/*" onChange={(e) => { const file = e.target.files?.[0]; setPhotoFile(file || null); if (file) setPreview(URL.createObjectURL(file)); }} /></label>
            <button className="green-button" type="submit">Save profile</button>
          </form>
        </section>
        <aside className="stack">
          <form className="panel form-stack" onSubmit={saveLocation}>
            <h2>Service location</h2>
            <p className="muted">Search your town or address and the coordinates will be filled automatically.</p>
            <label>Location search<input type="search" placeholder="Enter city or street" value={locationSearch} ref={locationSearchRef} onChange={(e) => handleLocationSearchChange(e.target.value)} /></label>
            <label>Latitude<input type="number" step="any" required readOnly value={location.latitude} /></label>
            <label>Longitude<input type="number" step="any" required readOnly value={location.longitude} /></label>
            <button className="green-button">Save location</button>
          </form>
          <form className="panel form-stack" onSubmit={saveRadius}>
            <h2>Service radius</h2>
            <label>Radius in kilometres<input type="number" min="0.1" max="100" step="0.1" required value={radius} onChange={(e) => setRadius(e.target.value)} /></label>
            <button className="outline-button">Save radius</button>
          </form>
        </aside>
      </div>}
    </DashboardShell>
  );
}
