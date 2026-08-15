import api from "./axios";

export async function addAvailability(providerId, data) {
  const response = await api.post(`/providers/${providerId}/availability`, data);
  return response.data;
}

export async function updateAvailability(id, data) {
  const response = await api.put(`/providers/availability/${id}`, data);
  return response.data;
}

export async function deleteAvailability(id) {
  const response = await api.delete(`/providers/availability/${id}`);
  return response.data;
}
