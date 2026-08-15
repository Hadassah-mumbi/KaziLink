import { useEffect, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import BookingCard from "../../components/BookingCard";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import { getProviderBookings, acceptBooking, rejectBooking, completeBooking } from "../../api/bookings";
import { getApiError } from "../../api/axios";

export default function ProviderBookings() {
  const [bookings, setBookings] = useState(null);
  const [error, setError] = useState("");
  const load = () => getProviderBookings().then(setBookings).catch((e) => setError(getApiError(e)));

  useEffect(() => {
    load();
  }, []);

  async function action(fn, id) {
    try {
      await fn(id);
      load();
    } catch (e) {
      setError(getApiError(e));
    }
  }

  return (
    <DashboardShell type="provider" title="Bookings" subtitle="Review incoming requests and manage your current bookings.">
      <ErrorMessage message={error} />
      {bookings === null ? <Loading /> : bookings.length ? <div className="stack">{bookings.map((b) => <BookingCard key={b.id} booking={b} role="provider" onAction={(booking) => (
        <>
          {booking.status === "pending" && <>
            <button className="green-button small" onClick={() => action(acceptBooking, booking.id)}>Accept</button>
            <button className="danger-button small" onClick={() => action(rejectBooking, booking.id)}>Reject</button>
          </>}
          {booking.status === "accepted" && <button className="green-button small" onClick={() => action(completeBooking, booking.id)}>Mark completed</button>}
        </>
      )} />)}</div> : <div className="empty-state"><h3>No bookings yet</h3><p>Incoming customer requests will appear here.</p></div>}
    </DashboardShell>
  );
}
