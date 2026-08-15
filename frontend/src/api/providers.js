import api from "./axios";

export async function searchProviders(params = {}) {
  const clean = Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined)
  );
  const response = await api.get("/providers/search", { params: clean });
  return response.data;
}

export async function getProvider(id) {
  const response = await api.get(`/providers/${id}`);
  return response.data;
}

export async function getMyProvider() {
  const response = await api.get("/providers/me");
  return response.data;
}

export async function updateProviderProfile(data) {
  const formData = new FormData();

  if (data.bio !== undefined) formData.append("bio", data.bio);
  if (data.county !== undefined) formData.append("county", data.county);
  if (data.town !== undefined) formData.append("town", data.town);
  if (data.experience_years !== undefined) formData.append("experience_years", data.experience_years);
  if (data.hourly_rate !== undefined) formData.append("hourly_rate", data.hourly_rate);
  if (data.daily_rate !== undefined) formData.append("daily_rate", data.daily_rate);
  if (data.profile_picture) formData.append("profile_picture", data.profile_picture);

  const response = await api.put("/providers/me", formData);
  return response.data;
}

export async function applyAsProvider(data) {
  const response = await api.post("/providers/apply", data);
  return response.data;
}

export async function updateProviderLocation(data) {
  const response = await api.put("/providers/me/location", data);
  return response.data;
}

export async function searchNearbyProviders(data) {
  const response = await api.post("/providers/search/nearby", data);
  return response.data;
}

export async function updateServiceRadius(data) {
  const response = await api.put("/providers/me/service-radius", data);
  return response.data;
}

export async function getMyServices() {
  const response = await api.get("/providers/me/services");
  return response.data;
}

export async function addMyService(category_id) {
  const response = await api.post("/providers/me/services", { category_id });
  return response.data;
}

export async function removeMyService(category_id) {
  const response = await api.delete(`/providers/me/services/${category_id}`);
  return response.data;
}

export async function getProviderAvailability(providerId) {
  const response = await api.get(`/providers/${providerId}/availability`);
  return response.data;
}
