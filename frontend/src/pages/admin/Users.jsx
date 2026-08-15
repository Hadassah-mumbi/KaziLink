import { useEffect, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import { getAdminUsers, activateUser, deactivateUser } from "../../api/admin";
import { getApiError } from "../../api/axios";

export default function AdminUsers() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState("");
  const load = async () => {
    try {
      const result = await getAdminUsers();
      setUsers(result);
    } catch (e) {
      setError(getApiError(e));
    }
  };

  useEffect(() => {
    load();
  }, []);

  async function act(fn, id) { try { await fn(id); load(); } catch (e) { setError(getApiError(e)); } }

  return (
    <DashboardShell type="admin" title="Users" subtitle="Manage active and inactive KaziLink accounts.">
      <ErrorMessage message={error} />
      {users === null ? <Loading /> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Name</th><th>Contact</th><th>Role</th><th>Status</th><th></th></tr></thead><tbody>
        {users.map((u) => <tr key={u.id}><td><strong>{u.first_name} {u.last_name}</strong><small>{u.id}</small></td><td>{u.email}<br />{u.phone}</td><td>{u.is_admin ? "Admin" : u.is_provider ? "Provider" : "Customer"}</td><td><span className={`status-badge ${u.is_active ? "status-accepted" : "status-cancelled"}`}>{u.is_active ? "Active" : "Inactive"}</span></td><td>{u.is_admin ? <span className="muted">Admin</span> : u.is_active ? <button className="danger-button small" onClick={() => act(deactivateUser, u.id)}>Deactivate</button> : <button className="green-button small" onClick={() => act(activateUser, u.id)}>Activate</button>}</td></tr>)}
      </tbody></table></div>}
    </DashboardShell>
  );
}
