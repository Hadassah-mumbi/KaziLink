import api from "./axios";

export async function createReview(data) {
  const response = await api.post("/reviews", data);
  return response.data;
}

export async function createProviderReview(data) {
  const response = await api.post("/reviews/provider/review", data);
  return response.data;
}

export async function getProviderReviews(providerId) {
  const response = await api.get(`/reviews/provider/${providerId}`);
  return response.data;
}

export async function getMyReviews() {
  const response = await api.get("/reviews/me");
  return response.data;
}

export async function getCustomerReviews(customerId) {
  const response = await api.get(`/reviews/customer/${customerId}`);
  return response.data;
}
