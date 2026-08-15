import api from "./axios";

export async function getCurrentUser() {
  const response = await api.get("/users/me");
  return response.data;
}

export async function updateCurrentUser(formData) {
  // send multipart form data to update profile
  const response = await api.put("/users/me", formData);
  return response.data;
}
