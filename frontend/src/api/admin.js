import api from "./axios";

export async function getAdminProviders() {
  const response = await api.get("/admin/providers");
  return response.data;
}

export async function getPendingProviders() {
  const response = await api.get("/admin/providers/pending");
  return response.data;
}

export async function getAdminProvider(id) {
  const response = await api.get(`/admin/providers/${id}`);
  return response.data;
}

export async function approveProvider(id) {
  const response = await api.put(`/admin/providers/${id}/approve`);
  return response.data;
}

export async function rejectProvider(id) {
  const response = await api.put(`/admin/providers/${id}/reject`);
  return response.data;
}

export async function getAdminUsers() {
  const response = await api.get("/admin/users");
  return response.data;
}

export async function activateUser(id) {
  const response = await api.put(`/admin/users/${id}/activate`);
  return response.data;
}

export async function deactivateUser(id) {
  const response = await api.put(`/admin/users/${id}/deactivate`);
  return response.data;
}
