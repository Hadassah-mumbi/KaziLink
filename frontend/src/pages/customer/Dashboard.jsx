import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import BookingCard from "../../components/BookingCard";
import Loading from "../../components/Loading";
import { getCustomerBookings } from "../../api/bookings";
import { getApiError } from "../../api/axios";
import ErrorMessage from "../../components/ErrorMessage";
import { useAuth } from "../../context/AuthContext";

export default function Dashboard() {
  const { currentUser } = useAuth();
  const [bookings, setBookings] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { getCustomerBookings().then(setBookings).catch((e) => setError(getApiError(e))); }, []);

  return (
    <DashboardShell
      type="customer"
      title={`Hello, ${currentUser?.first_name || "there"} 👋`}
      subtitle="Here is what is happening with your KaziLink bookings."
      actions={<Link to="/" className="outline-button">Back to home</Link>}
    >
      <ErrorMessage message={error} />
      <div className="quick-grid">
        <Link to="/providers" className="quick-card"><span>Find a provider</span><strong>Browse services →</strong></Link>
        <Link to="/dashboard/bookings" className="quick-card"><span>Your bookings</span><strong>View all →</strong></Link>
      </div>
      <section className="dashboard-section">
        <div className="section-row"><h2>Recent bookings</h2><Link to="/dashboard/bookings">View all</Link></div>
        {bookings === null ? <Loading /> : bookings.length ? bookings.slice(0, 3).map((b) => <BookingCard key={b.id} booking={b} />) : <div className="empty-state"><h3>No bookings yet</h3><p>Find a provider and make your first booking.</p><Link to="/providers" className="green-button">Find a provider</Link></div>}
      </section>
    </DashboardShell>
  );
}
