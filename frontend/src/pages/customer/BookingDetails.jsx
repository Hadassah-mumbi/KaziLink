import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";
import ErrorBoundary from "../../components/ErrorBoundary";
import StatusBadge from "../../components/StatusBadge";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import { getBooking, cancelBooking, downloadAcceptanceDocument } from "../../api/bookings";
import { getApiError } from "../../api/axios";

export default function BookingDetails() {
  const { bookingId } = useParams();
  const [booking, setBooking] = useState(null);
  const [error, setError] = useState("");

  const load = () => getBooking(bookingId).then(setBooking).catch((e) => setError(getApiError(e)));
  useEffect(() => {
    // Call loader from inside effect instead of passing the promise-returning function
    load();
  }, [bookingId]);

  async function cancel() {
    if (!window.confirm("Cancel this booking?")) return;
    try { await cancelBooking(bookingId); load(); } catch (e) { setError(getApiError(e)); }
  }

  if (!booking && !error) return (
    <ErrorBoundary>
      <DashboardShell type="customer" title="Booking details">
        <Loading />
      </DashboardShell>
    </ErrorBoundary>
  );

  return (
    <ErrorBoundary>
      <DashboardShell type="customer" title="Booking details">
        <ErrorMessage message={error} />
        {booking && <div className="details-layout">
          <section className="panel">
            <div className="section-row"><div><p className="eyebrow">Booking</p><h2>{booking.category_name || "Service booking"}</h2></div><StatusBadge status={booking.status} /></div>
            <div className="booking-provider-card">
              <div className="avatar">
                {booking.provider_profile_picture ? (
                  <img src={booking.provider_profile_picture} alt={booking.provider_name || "Provider"} />
                ) : (
                  <span>{booking.provider_name ? booking.provider_name.charAt(0) : "P"}</span>
                )}
              </div>
              <div>
                <strong>{booking.provider_name || "Provider"}</strong>
                {booking.provider_phone && <p className="muted">Contact: <a href={`tel:${booking.provider_phone}`}>{booking.provider_phone}</a></p>}
                <Link to={`/providers/${booking.provider_id}`} className="text-button">View provider profile</Link>
              </div>
            </div>
            <div className="details-grid">
              <div><span>Date</span><strong>{booking.booking_date}</strong></div>
              <div><span>Time</span><strong>{String(booking.booking_time).slice(0,5)}</strong></div>
              <div><span>County</span><strong>{booking.county}</strong></div>
              <div><span>Town</span><strong>{booking.town}</strong></div>
              <div><span>Address</span><strong>{booking.address || "Not provided"}</strong></div>
            </div>
            <div className="detail-description"><span>Description</span><p>{booking.description || "No description provided."}</p></div>
            <div className="inline-actions">
              {(booking.status === "pending" || booking.status === "accepted") && <button className="danger-button" onClick={cancel}>Cancel booking</button>}
              {booking.status === "accepted" && <button className="green-button" onClick={async () => {
                try {
                  const blob = await downloadAcceptanceDocument(bookingId);
                  const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `booking_${bookingId}.pdf`;
                  document.body.appendChild(a);
                  a.click();
                  a.remove();
                  window.URL.revokeObjectURL(url);
                } catch (e) {
                  setError(getApiError(e));
                }
              }}>Download acceptance document</button>}
              {booking.status === "completed" && <Link className="green-button" to={`/dashboard/bookings/${booking.id}/review`}>Review provider</Link>}
            </div>
          </section>
        </div>}
      </DashboardShell>
    </ErrorBoundary>
  );
}
