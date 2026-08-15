import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import StatusBadge from "../../components/StatusBadge";
import { getBooking } from "../../api/bookings";
import { getApiError } from "../../api/axios";
import { createProviderReview } from "../../api/reviews";

export default function BookingDetails() {
  const { bookingId } = useParams();
  const [booking, setBooking] = useState(null);
  const [error, setError] = useState("");
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [reviewing, setReviewing] = useState(false);
  const [reviewSubmitted, setReviewSubmitted] = useState(false);

  useEffect(() => {
    getBooking(bookingId)
      .then(setBooking)
      .catch((e) => setError(getApiError(e)));
  }, [bookingId]);

  async function submitReview(e) {
    e.preventDefault();
    setReviewing(true);
    setError("");
    try {
      await createProviderReview({
        booking_id: bookingId,
        rating: parseInt(rating),
        comment: comment || null,
      });
      setReviewSubmitted(true);
      setComment("");
      setRating(5);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setReviewing(false);
    }
  }

  if (!booking && !error) return <DashboardShell type="provider" title="Booking details"><Loading /></DashboardShell>;
  return <DashboardShell type="provider" title="Booking details"><ErrorMessage message={error} />{booking && <section className="panel">
        <div className="section-row">
          <div>
            <p className="eyebrow">Booking</p>
            <h2>{booking.category_name || "Service booking"}</h2>
          </div>
          <StatusBadge status={booking.status} />
        </div>

        <div className="booking-person-card">
          <div className="avatar-circle avatar-circle--small">
            {booking.customer_profile_picture ? <img src={booking.customer_profile_picture} alt={booking.customer_name || "Customer"} /> : <span>{booking.customer_name?.charAt(0) || "C"}</span>}
          </div>
          <div>
            <p className="eyebrow">Customer</p>
            <strong>{booking.customer_name || "Customer"}</strong>
            {booking.customer_phone && <p className="muted">{booking.customer_phone}</p>}
          </div>
        </div>

        <div className="details-grid">
          <div><span>Date</span><strong>{booking.booking_date}</strong></div>
          <div><span>Time</span><strong>{String(booking.booking_time).slice(0,5)}</strong></div>
          <div><span>Location</span><strong>{booking.town}, {booking.county}</strong></div>
          <div><span>Address</span><strong>{booking.address || "Not provided"}</strong></div>
        </div>
        <div className="detail-description"><span>Description</span><p>{booking.description || "No description provided."}</p></div>

        {booking.status === "completed" && !reviewSubmitted && (
          <div className="review-form-container" style={{ marginTop: "30px", paddingTop: "30px", borderTop: "1px solid #e0e0e0" }}>
            <h3>Review this customer</h3>
            <form onSubmit={submitReview}>
              <div style={{ marginBottom: "15px" }}>
                <label>Rating</label>
                <div style={{ display: "flex", gap: "10px", marginTop: "8px" }}>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setRating(star)}
                      style={{
                        fontSize: "28px",
                        border: "none",
                        background: "none",
                        cursor: "pointer",
                        opacity: rating >= star ? 1 : 0.3,
                        transition: "opacity 0.2s",
                      }}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>
              <label>
                Comment (optional)
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  maxLength={500}
                  rows={4}
                  placeholder="Share your experience with this customer..."
                />
              </label>
              <button type="submit" className="green-button" disabled={reviewing}>
                {reviewing ? "Submitting..." : "Submit review"}
              </button>
            </form>
          </div>
        )}

        {reviewSubmitted && (
          <div style={{ marginTop: "30px", padding: "15px", background: "#d4edda", color: "#155724", borderRadius: "4px", border: "1px solid #c3e6cb" }}>
            <strong>✓ Review submitted!</strong> Thank you for your feedback about this customer.
          </div>
        )}
      </section>}</DashboardShell>;
}
