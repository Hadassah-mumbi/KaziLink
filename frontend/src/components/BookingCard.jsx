import { Link } from "react-router-dom";
import { CalendarDays, Clock3, MapPin } from "lucide-react";
import StatusBadge from "./StatusBadge";

export default function BookingCard({ booking, role = "customer", onAction }) {
  return (
    <article className="booking-card">
      <div className="booking-card-top">
        <div>
          <p className="eyebrow">{role === "provider" ? "Customer booking" : "Service booking"}</p>
          <h3>{booking.category_name || "Service booking"}</h3>
        </div>
        <StatusBadge status={booking.status} />
      </div>

      <div className="booking-person-card">
        <div className="avatar-circle">
          {role === "provider" ? (
            booking.customer_profile_picture ? <img src={booking.customer_profile_picture} alt={booking.customer_name || "Customer"} /> : <span>{booking.customer_name?.charAt(0) || "C"}</span>
          ) : (
            booking.provider_profile_picture ? <img src={booking.provider_profile_picture} alt={booking.provider_name || "Provider"} /> : <span>{booking.provider_name?.charAt(0) || "P"}</span>
          )}
        </div>
        <div>
          <p className="eyebrow">{role === "provider" ? "Customer" : "Provider"}</p>
          <strong>{role === "provider" ? booking.customer_name || "Customer" : booking.provider_name || "Provider"}</strong>
          <p className="muted">{role === "provider" ? booking.customer_phone : booking.provider_phone}</p>
        </div>
      </div>

      <div className="booking-meta-grid">
        <span><CalendarDays size={15} /> {booking.booking_date}</span>
        <span><Clock3 size={15} /> {String(booking.booking_time).slice(0, 5)}</span>
        <span><MapPin size={15} /> {booking.town}, {booking.county}</span>
      </div>

      {booking.description && <p className="booking-description">{booking.description}</p>}

      <div className="booking-card-actions">
        <Link to={`${role === "provider" ? "/provider/bookings/" : "/dashboard/bookings/"}${booking.id}`} className="text-button">
          View details
        </Link>

        {onAction && <div className="inline-actions">{onAction(booking)}</div>}
      </div>
    </article>
  );
}
