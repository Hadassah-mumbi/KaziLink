import { useEffect, useMemo, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import BookingCard from "../../components/BookingCard";
import StatusBadge from "../../components/StatusBadge";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import { getCustomerBookings, cancelBooking } from "../../api/bookings";
import { getApiError } from "../../api/axios";

export default function Bookings() {
  const [bookings, setBookings] = useState(null);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");

  const load = () => getCustomerBookings().then(setBookings).catch((e) => setError(getApiError(e)));
  useEffect(() => {
    console.log("Bookings: loading...");
    load();
  }, []);

  const filtered = useMemo(() => filter === "all" ? bookings || [] : (bookings || []).filter((b) => b.status === filter), [bookings, filter]);

  async function cancel(id) {
    if (!window.confirm("Cancel this booking?")) return;
    try { await cancelBooking(id); load(); } catch (e) { setError(getApiError(e)); }
  }

  return (
    <DashboardShell type="customer" title="My bookings" subtitle="Track every request, accepted booking and completed service.">
      <ErrorMessage message={error} />
      <div className="status-filters">
        {["all","pending","accepted","rejected","cancelled","completed"].map((s) => <button key={s} className={filter === s ? "active" : ""} onClick={() => setFilter(s)}>{s === "all" ? "All" : <StatusBadge status={s} />}</button>)}
      </div>
      {bookings === null ? <Loading /> : filtered.length ? <div className="stack">{filtered.map((b) => <BookingCard key={b.id} booking={b} onAction={(booking) => (
        (booking.status === "pending" || booking.status === "accepted") ? <button className="danger-button small" onClick={() => cancel(booking.id)}>Cancel</button> : null
      )} />)}</div> : <div className="empty-state"><h3>No {filter === "all" ? "" : filter} bookings</h3><p>There is nothing to show here yet.</p></div>}
    </DashboardShell>
  );
}

