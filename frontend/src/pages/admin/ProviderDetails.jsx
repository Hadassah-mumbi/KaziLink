import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import StatusBadge from "../../components/StatusBadge";
import { getAdminProvider, approveProvider, rejectProvider } from "../../api/admin";
import { getApiError } from "../../api/axios";

export default function AdminProviderDetails() {
  const { providerId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const result = await getAdminProvider(providerId);
      setData(result);
    } catch (e) {
      setError(getApiError(e));
    }
  };

  useEffect(() => {
    load();
  }, [providerId]);

  async function act(fn) { try { await fn(providerId); load(); } catch (e) { setError(getApiError(e)); } }

  if (!data && !error) return <DashboardShell type="admin" title="Provider details"><Loading /></DashboardShell>;

  const p = data?.provider;
  const u = data?.user;

  return (
    <DashboardShell type="admin" title="Provider details">
      <ErrorMessage message={error} />
      {p && <div className="profile-grid">
        <section className="panel">
          <div className="section-row"><div><p className="eyebrow">Application</p><h2>{u?.first_name} {u?.last_name}</h2><p className="muted">{u?.email} · {u?.phone}</p></div><StatusBadge status={p.approved ? "accepted" : "pending"} /></div>
          <h3>About</h3><p>{p.bio}</p>
          <div className="details-grid"><div><span>County</span><strong>{p.county}</strong></div><div><span>Town</span><strong>{p.town}</strong></div><div><span>Experience</span><strong>{p.experience_years} years</strong></div><div><span>Hourly</span><strong>KSh {Number(p.hourly_rate).toLocaleString()}</strong></div><div><span>Daily</span><strong>KSh {Number(p.daily_rate).toLocaleString()}</strong></div></div>
          <div className="details-grid"><div><span>Documents</span><strong><StatusBadge status={p.national_id_document && p.good_conduct_certificate ? "uploaded" : "missing"} /></strong></div></div>
          <h3>Documents</h3>
          <div className="details-grid">
            <div>
              <span>National ID</span>
              <strong>{p.national_id_document ? <a href={p.national_id_document} target="_blank" rel="noreferrer">View document</a> : "Not provided"}</strong>
            </div>
            <div>
              <span>Good conduct certificate</span>
              <strong>{p.good_conduct_certificate ? <a href={p.good_conduct_certificate} target="_blank" rel="noreferrer">View document</a> : "Not provided"}</strong>
            </div>
          </div>
          <h3>Services</h3><div className="tag-list">{p.services?.map((s) => <span className="service-tag" key={s.category_id}>{s.name}</span>)}</div>
          <div className="inline-actions">{!p.approved && <button className="green-button" onClick={() => act(approveProvider)}>Approve provider</button>}{p.approved && <button className="danger-button" onClick={() => act(rejectProvider)}>Reject provider</button>}<button className="outline-button" onClick={() => navigate("/admin/providers")}>Back</button></div>
        </section>
      </div>}
    </DashboardShell>
  );
}
