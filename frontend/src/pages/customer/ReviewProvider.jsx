import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";
import ErrorMessage from "../../components/ErrorMessage";
import { createReview } from "../../api/reviews";
import { getApiError } from "../../api/axios";

export default function ReviewProvider() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault(); setError(""); setBusy(true);
    try { await createReview({ booking_id: bookingId, rating: Number(rating), comment: comment || null }); navigate(`/dashboard/bookings/${bookingId}`); }
    catch (e) { setError(getApiError(e)); }
    finally { setBusy(false); }
  }

  return (
    <DashboardShell type="customer" title="Review your provider" subtitle="Your feedback is attached to the completed booking.">
      <form className="panel review-form" onSubmit={submit}>
        <ErrorMessage message={error} />
        <label>Rating</label>
        <div className="rating-picker">
          {[1,2,3,4,5].map((n) => <button type="button" key={n} className={n <= rating ? "selected" : ""} onClick={() => setRating(n)}>★</button>)}
        </div>
        <label>Comment (optional)<textarea rows="6" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Tell us about your experience..." /></label>
        <button className="green-button" disabled={busy}>{busy ? "Submitting review..." : "Submit review"}</button>
      </form>
    </DashboardShell>
  );
}
