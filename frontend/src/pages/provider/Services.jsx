import { useEffect, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import ErrorMessage from "../../components/ErrorMessage";
import Loading from "../../components/Loading";
import { getCategories } from "../../api/categories";
import { addMyService, getMyServices, removeMyService } from "../../api/providers";
import { getApiError } from "../../api/axios";

export default function ProviderServices() {
  const [services, setServices] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selected, setSelected] = useState("");
  const [error, setError] = useState("");

  const load = () => Promise.all([getMyServices(), getCategories()])
    .then(([s, c]) => { setServices(s); setCategories(c); })
    .catch((e) => setError(getApiError(e)));

  useEffect(() => {
    load();
  }, []);

  async function add() {
    if (!selected) return;
    try {
      await addMyService(selected);
      setSelected("");
      load();
    } catch (e) {
      setError(getApiError(e));
    }
  }
  async function remove(id) { try { await removeMyService(id); load(); } catch (e) { setError(getApiError(e)); } }

  const available = categories.filter((c) => !services?.some((s) => s.category_id === c.id));

  return (
    <DashboardShell type="provider" title="My services" subtitle="Choose the service categories you offer to customers.">
      <ErrorMessage message={error} />
      {services === null ? <Loading /> : <div className="two-column">
        <section className="panel">
          <h2>Current services</h2>
          {services.length ? <div className="tag-list">{services.map((s) => <span className="service-tag removable" key={s.category_id}>{s.name}<button onClick={() => remove(s.category_id)}>×</button></span>)}</div> : <p className="muted">You have not selected any services yet.</p>}
        </section>
        <section className="panel form-stack">
          <h2>Add a service</h2>
          <select value={selected} onChange={(e) => setSelected(e.target.value)}>
            <option value="">Choose category</option>
            {available.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <button className="green-button" onClick={add}>Add service</button>
        </section>
      </div>}
    </DashboardShell>
  );
}
