import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import RatingStars from "../components/RatingStars";
import { getProvider, getProviderAvailability } from "../api/providers";
import { getProviderReviews } from "../api/reviews";
import { getApiError } from "../api/axios";

const days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

export default function ProviderDetails() {
  const { providerId } = useParams();
  const [provider, setProvider] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [availability, setAvailability] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getProvider(providerId), getProviderReviews(providerId), getProviderAvailability(providerId)])
      .then(([p, r, a]) => { setProvider(p); setReviews(r); setAvailability(a); })
      .catch((e) => setError(getApiError(e)));
  }, [providerId]);

  if (error) {
    return <><Navbar /><main className="content-page"><ErrorMessage message={error} /></main></>;
  }

  if (!provider) {
    return <><Navbar /><Loading label="Loading provider profile..." /></>;
  }

  return (
    <>
      <Navbar />
      <main className="profile-page">
        <section className="profile-header">
          <div className="large-avatar">
            {provider.profile_picture ? (
              <img src={provider.profile_picture} alt={provider.name || "Provider"} />
            ) : (
              provider.name?.charAt(0) || "P"
            )}
          </div>
          <div>
            <p className="eyebrow">{provider.name || "KaziLink provider"}</p>
            <h1>{provider.name || "Professional Service Provider"}</h1>
            <div className="provider-rating">
              <RatingStars value={provider.average_rating} />
              <strong>{Number(provider.average_rating || 0).toFixed(1)}</strong>
              <span>{provider.total_reviews || 0} reviews</span>
            </div>
            <p className="muted">{provider.town}, {provider.county} · {provider.experience_years} years experience</p>
            {provider.phone && (
              <p className="muted">Contact: <a href={`tel:${provider.phone}`}>{provider.phone}</a></p>
            )}
          </div>
          <div className="profile-cta">
            <Link to={`/providers/${provider.id}/book`} className="green-button">Book provider</Link>
          </div>
        </section>

        <div className="profile-grid">
          <div className="profile-main">
            <section className="panel">
              <h2>About me</h2>
              <p>{provider.bio}</p>
            </section>
            <section className="panel">
              <h2>Services</h2>
              <div className="tag-list">
                {provider.services?.map((s) => (
                  <span key={s.category_id} className="service-tag">{s.name}</span>
                ))}
              </div>
            </section>
            <section className="panel">
              <h2>Reviews</h2>
              {reviews.length ? reviews.map((review) => (
                <div className="review-row" key={review.id}>
                  <div className="review-avatar">{review.rating}</div>
                  <div>
                    <RatingStars value={review.rating} />
                    <p>{review.comment || "No comment provided."}</p>
                    <small>{new Date(review.created_at).toLocaleDateString()}</small>
                  </div>
                </div>
              )) : <p className="muted">No reviews yet.</p>}
            </section>
          </div>

          <aside className="profile-side">
            <div className="panel">
              <h2>Rates</h2>
              <div className="rate-row"><span>Hourly</span><strong>KSh {Number(provider.hourly_rate).toLocaleString()}</strong></div>
              <div className="rate-row"><span>Daily</span><strong>KSh {Number(provider.daily_rate).toLocaleString()}</strong></div>
            </div>
            <div className="panel">
              <h2>Availability</h2>
              {availability.length ? availability.map((a) => (
                <div className="availability-row" key={a.id}>
                  <span>{days[a.day_of_week]}</span>
                  <span>{a.is_available ? `${String(a.start_time).slice(0,5)} – ${String(a.end_time).slice(0,5)}` : "Unavailable"}</span>
                </div>
              )) : <p className="muted">No availability has been configured yet.</p>}
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </>
  );
}
