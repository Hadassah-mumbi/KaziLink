import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import BookingCard from "../../components/BookingCard";
import StatusBadge from "../../components/StatusBadge";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import { getMyProvider } from "../../api/providers";
import { getProviderBookings } from "../../api/bookings";
import { getApiError } from "../../api/axios";

export default function ProviderDashboard() {
  const [provider, setProvider] = useState(null);
  const [bookings, setBookings] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getMyProvider(), getProviderBookings()])
      .then(([p, b]) => { setProvider(p); setBookings(b); })
      .catch((e) => setError(getApiError(e)));
  }, []);

  return (
    <DashboardShell
      type="provider"
      title="Provider dashboard"
      subtitle="Manage your profile, availability and incoming work."
      actions={<Link to="/" className="outline-button">Back to home</Link>}
    >
      <ErrorMessage message={error} />
      {provider && <div className="provider-status-banner"><div><span className="eyebrow">Application status</span><h2>{provider.approved ? "Approved and visible to customers" : "Pending administrator approval"}</h2></div><StatusBadge status={provider.approved ? "accepted" : "pending"} /></div>}
      <div className="stats-grid simple">
        <div className="mini-stat"><span>Completed jobs</span><strong>{provider?.completed_jobs ?? "—"}</strong></div>
        <div className="mini-stat"><span>Average rating</span><strong>{provider ? Number(provider.average_rating || 0).toFixed(1) : "—"}</strong></div>
        <div className="mini-stat"><span>Total reviews</span><strong>{provider?.total_reviews ?? "—"}</strong></div>
      </div>
      <section className="dashboard-section">
        <div className="section-row"><h2>Booking requests</h2><a href="/provider/bookings">View all</a></div>
        {bookings === null ? <Loading /> : bookings.length ? bookings.slice(0,4).map((b) => <BookingCard key={b.id} booking={b} role="provider" />) : <div className="empty-state"><h3>No bookings yet</h3><p>New booking requests will appear here.</p></div>}
      </section>
    </DashboardShell>
  );
}
