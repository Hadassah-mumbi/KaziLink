import api from "./axios";

export async function registerCustomer(data) {
  const response = await api.post("/auth/register/customer", data);
  return response.data;
}

export async function loginUser(email, password) {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const response = await api.post("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data;
}
