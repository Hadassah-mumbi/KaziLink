import { useAuth } from "../../context/AuthContext";
import DashboardShell from "../../components/DashboardShell";
import { useEffect, useState } from "react";
import { updateCurrentUser } from "../../api/users";
import { getApiError } from "../../api/axios";

export default function Profile() {
  const { currentUser, refreshUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [firstName, setFirstName] = useState(currentUser?.first_name || "");
  const [lastName, setLastName] = useState(currentUser?.last_name || "");
  const [phone, setPhone] = useState(currentUser?.phone || "");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(currentUser?.profile_picture || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setFirstName(currentUser?.first_name || "");
    setLastName(currentUser?.last_name || "");
    setPhone(currentUser?.phone || "");
    setPreview(currentUser?.profile_picture || null);
  }, [currentUser]);

  const uploadPhoto = async (photoFile) => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("profile_picture", photoFile);
      const updated = await updateCurrentUser(formData);
      setPreview(updated.profile_picture || URL.createObjectURL(photoFile));
      await refreshUser();
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    setFile(f || null);
    if (f) {
      setPreview(URL.createObjectURL(f));
      uploadPhoto(f);
      setEditing(true);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("first_name", firstName);
      formData.append("last_name", lastName);
      formData.append("phone", phone);
      if (file) formData.append("profile_picture", file);

      await updateCurrentUser(formData);
      await refreshUser();
      setEditing(false);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardShell type="customer" title="My profile" subtitle="Your current account information.">
      <section className="panel profile-summary">
        <div className="large-avatar">
          {preview ? <img src={preview} alt="avatar" /> : (currentUser?.first_name?.[0] || "K")}
        </div>

        {!editing ? (
          <div>
            <h2>{currentUser?.first_name} {currentUser?.last_name}</h2>
            <p>{currentUser?.email}</p>
            <p>{currentUser?.phone}</p>
            <div style={{ marginTop: 12 }}>
              <button className="green-button" onClick={() => setEditing(true)}>Edit profile</button>
            </div>
          </div>
        ) : (
          <form onSubmit={submit} style={{ display: 'grid', gap: 12 }}>
            <div style={{ display: 'grid', gap: 8 }}>
              <label>First name</label>
              <input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
              <label>Last name</label>
              <input value={lastName} onChange={(e) => setLastName(e.target.value)} />
              <label>Phone</label>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>

            <div>
              <label>Profile photo</label>
              <input type="file" accept="image/*" onChange={handleFile} />
            </div>

            {error && <div className="error-message">{error}</div>}

            <div style={{ display: 'flex', gap: 8 }}>
              <button type="submit" className="green-button" disabled={loading}>{loading ? "Saving..." : "Save"}</button>
              <button type="button" className="text-button" onClick={() => { setEditing(false); setPreview(currentUser?.profile_picture || null); }}>Cancel</button>
            </div>
            {file && !loading && <div style={{ color: '#2d6b35', fontSize: 13 }}>Profile photo upload saved automatically.</div>}
          </form>
        )}
      </section>
    </DashboardShell>
  );
}
