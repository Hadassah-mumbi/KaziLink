import { useEffect, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import ErrorMessage from "../../components/ErrorMessage";
import { addAvailability, deleteAvailability, updateAvailability } from "../../api/availability";
import { getMyProvider, getProviderAvailability } from "../../api/providers";
import { getApiError } from "../../api/axios";

const days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

export default function Availability() {
  const [provider, setProvider] = useState(null);
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ category_id: "", day_of_week: 0, start_time: "08:00", end_time: "17:00" });

  const load = async () => {
    try {
      const p = await getMyProvider();
      setProvider(p);
      if (p.services && p.services.length && !form.category_id) {
        setForm((current) => ({ ...current, category_id: p.services[0].category_id }));
      }
      setRecords(await getProviderAvailability(p.id));
    } catch (e) {
      setError(getApiError(e));
    }
  };
  useEffect(() => { load(); }, []);

  async function add() {
    try {
      await addAvailability(provider.id, {
        ...form,
        day_of_week: Number(form.day_of_week),
      });
      load();
    } catch (e) {
      setError(getApiError(e));
    }
  }

  async function toggle(record) {
    try {
      await updateAvailability(record.id, {
        category_id: record.category_id,
        day_of_week: record.day_of_week,
        start_time: record.start_time,
        end_time: record.end_time,
        is_available: !record.is_available,
      });
      load();
    } catch (e) {
      setError(getApiError(e));
    }
  }

  async function remove(id) { try { await deleteAvailability(id); load(); } catch (e) { setError(getApiError(e)); } }

  return (
    <DashboardShell type="provider" title="Availability" subtitle="Set the days and hours when you can receive bookings.">
      <ErrorMessage message={error} />
      <div className="two-column">
        <section className="panel">
          <h2>Weekly schedule</h2>
          {days.map((day, i) => {
            const record = records.find((r) => r.day_of_week === i);
            return <div className="schedule-row" key={day}>
              <strong>{day}</strong>
              {record ? <><span>{record.is_available ? `${String(record.start_time).slice(0,5)} – ${String(record.end_time).slice(0,5)}` : "Unavailable"}</span><div className="inline-actions"><button className="text-button" onClick={() => toggle(record)}>{record.is_available ? "Disable" : "Enable"}</button><button className="danger-text" onClick={() => remove(record.id)}>Remove</button></div></> : <span className="muted">Not set</span>}
            </div>;
          })}
        </section>
        <section className="panel form-stack">
          <h2>Add availability</h2>
          <label>Service category<select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
            <option value="">Select category</option>
            {provider?.services?.map((service) => (
              <option key={service.category_id} value={service.category_id}>{service.name}</option>
            ))}
          </select></label>
          <label>Day<select value={form.day_of_week} onChange={(e) => setForm({ ...form, day_of_week: e.target.value })}>{days.map((d, i) => <option key={d} value={i}>{d}</option>)}</select></label>
          <label>Start time<input type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} /></label>
          <label>End time<input type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} /></label>
          <button className="green-button" onClick={add}>Add to schedule</button>
        </section>
      </div>
    </DashboardShell>
  );
}
