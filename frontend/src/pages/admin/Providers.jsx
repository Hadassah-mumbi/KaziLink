import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import StatusBadge from "../../components/StatusBadge";
import { getAdminProviders, getPendingProviders, approveProvider, rejectProvider } from "../../api/admin";
import { getApiError } from "../../api/axios";

export default function AdminProviders() {
  const [providers, setProviders] = useState(null);
  const [error, setError] = useState("");
  const [params] = useSearchParams();
  const pendingOnly = params.get("pending") === "true";

  const load = async () => {
    try { setProviders(pendingOnly ? await getPendingProviders() : await getAdminProviders()); }
    catch (e) { setError(getApiError(e)); }
  };
  useEffect(() => { load(); }, [pendingOnly]);

  async function act(fn, id) { try { await fn(id); load(); } catch (e) { setError(getApiError(e)); } }

  return (
    <DashboardShell type="admin" title={pendingOnly ? "Pending provider applications" : "Providers"} subtitle="Review provider profiles and approval status.">
      <ErrorMessage message={error} />
      {providers === null ? <Loading /> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Provider</th><th>Location</th><th>Experience</th><th>Rate</th><th>Docs</th><th>Status</th><th></th></tr></thead><tbody>
        {providers.map((p) => {
          const docsStatus = p.national_id_document && p.good_conduct_certificate ? "uploaded" : "missing";
          return (
            <tr key={p.id}>
              <td><strong>Provider {String(p.id).slice(0,8)}</strong><small>{p.user_id}</small></td>
              <td>{p.town}, {p.county}</td>
              <td>{p.experience_years} years</td>
              <td>KSh {Number(p.hourly_rate).toLocaleString()}/hr</td>
              <td><StatusBadge status={docsStatus} /></td>
              <td><StatusBadge status={p.approved ? "accepted" : "pending"} /></td>
              <td><div className="inline-actions"><Link className="text-button" to={`/admin/providers/${p.id}`}>View</Link>{!p.approved ? <button className="green-button small" onClick={() => act(approveProvider, p.id)}>Approve</button> : <button className="danger-button small" onClick={() => act(rejectProvider, p.id)}>Reject</button>}</div></td>
            </tr>
          );
        })}
      </tbody></table></div>}
    </DashboardShell>
  );
}
