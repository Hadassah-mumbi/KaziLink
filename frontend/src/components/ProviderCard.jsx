import { Link } from "react-router-dom";
import { MapPin, BriefcaseBusiness } from "lucide-react";
import RatingStars from "./RatingStars";

export default function ProviderCard({ provider, onChoose }) {
  const name = provider.name || "KaziLink Provider";
  return (
    <article className="provider-card">
      <div className="provider-main">
        <div className="avatar">
          {provider.profile_picture ? (
            <img src={provider.profile_picture} alt={name} />
          ) : (
            <span>{name.charAt(0)}</span>
          )}
        </div>
        <div className="provider-info">
          <h3>{name}</h3>
          {provider.distance_km != null && (
            <p className="muted">Distance: {provider.distance_km} km</p>
          )}
          <div className="provider-rating">
            <RatingStars value={provider.average_rating} />
            <strong>{Number(provider.average_rating || 0).toFixed(1)}</strong>
            <span>({provider.total_reviews || 0} reviews)</span>
          </div>
          <p className="muted"><MapPin size={14} /> {provider.town}, {provider.county}</p>
          <p className="muted"><BriefcaseBusiness size={14} /> {provider.experience_years} years experience</p>
        </div>
      </div>

      <div className="provider-price">
        <strong>KSh {Number(provider.hourly_rate || 0).toLocaleString()}</strong>
        <span>/ hour</span>
      </div>

      <div className="provider-actions">
        <Link to={`/providers/${provider.id}`} className="text-button">View profile</Link>
        {onChoose ? (
          <button className="green-button small" onClick={() => onChoose(provider)}>Choose me</button>
        ) : (
          <Link to={`/providers/${provider.id}/book`} className="green-button small">Choose me</Link>
        )}
      </div>
    </article>
  );
}
