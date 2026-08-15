import api from "./axios";

export async function createBooking(data) {
  const response = await api.post("/bookings", data);
  return response.data;
}

export async function getBooking(id) {
  const response = await api.get(`/bookings/${id}`);
  return response.data;
}

export async function getCustomerBookings() {
  const response = await api.get("/bookings/customer/me");
  return response.data;
}

export async function getProviderBookings() {
  const response = await api.get("/bookings/provider/me");
  return response.data;
}

export async function acceptBooking(id) {
  const response = await api.put(`/bookings/${id}/accept`);
  return response.data;
}

export async function rejectBooking(id) {
  const response = await api.put(`/bookings/${id}/reject`);
  return response.data;
}

export async function completeBooking(id) {
  const response = await api.put(`/bookings/${id}/complete`);
  return response.data;
}

export async function updateBookingStatus(id, status) {
  const response = await api.put(`/bookings/${id}/status`, { status });
  return response.data;
}

export async function cancelBooking(id) {
  const response = await api.delete(`/bookings/${id}`);
  return response.data;
}

export async function downloadAcceptanceDocument(id) {
  const response = await api.get(`/bookings/${id}/acceptance_document`, { responseType: 'blob' });
  return response.data;
}
