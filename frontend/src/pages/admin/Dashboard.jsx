import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import DashboardShell from "../../components/DashboardShell";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import { getAdminProviders, getPendingProviders, getAdminUsers } from "../../api/admin";
import { getApiError } from "../../api/axios";

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [providers, pending, users] = await Promise.all([
          getAdminProviders(),
          getPendingProviders(),
          getAdminUsers(),
        ]);
        setData({ providers, pending, users });
      } catch (e) {
        setError(getApiError(e));
      }
    }

    loadDashboard();
  }, []);

  if (!data && !error) return <DashboardShell type="admin" title="Admin dashboard"><Loading /></DashboardShell>;

  const approved = data?.providers?.filter((p) => p.approved).length || 0;
  return (
    <DashboardShell
      type="admin"
      title="Admin dashboard"
      subtitle="Keep provider applications and user accounts organised."
      actions={<Link to="/" className="outline-button">Back to home</Link>}
    >
      <ErrorMessage message={error} />
      {data && <div className="stats-grid">
        <Link to="/admin/users" className="admin-stat"><span>Total users</span><strong>{data.users.length}</strong></Link>
        <Link to="/admin/providers" className="admin-stat"><span>Total providers</span><strong>{data.providers.length}</strong></Link>
        <Link to="/admin/providers" className="admin-stat"><span>Approved providers</span><strong>{approved}</strong></Link>
        <Link to="/admin/providers?pending=true" className="admin-stat"><span>Pending applications</span><strong>{data.pending.length}</strong></Link>
      </div>}
      <div className="admin-callouts">
        <Link to="/admin/providers" className="panel link-panel"><span>Provider management</span><strong>Review applications →</strong></Link>
        <Link to="/admin/users" className="panel link-panel"><span>User management</span><strong>Activate or deactivate users →</strong></Link>
      </div>
    </DashboardShell>
  );
}
