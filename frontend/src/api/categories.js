import api from "./axios";

export async function getCategories() {
  const response = await api.get("/categories");
  return response.data;
}

export async function getCategory(id) {
  const response = await api.get(`/categories/${id}`);
  return response.data;
}
