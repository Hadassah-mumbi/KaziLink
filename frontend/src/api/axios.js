import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("kazilink_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (!config.headers?.["Content-Type"] && !(config.data instanceof FormData)) {
    config.headers = { ...config.headers, "Content-Type": "application/json" };
  }

  config.metadata = { startTime: new Date() };
  return config;
});

export const getApiError = (error) => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || "Invalid value").join(", ");
  }
  return error?.message || "Something went wrong. Please try again.";
};

api.interceptors.response.use(
  (response) => {
    try {
      const start = response.config?.metadata?.startTime;
      if (start) {
        const duration = new Date() - new Date(start);
        // eslint-disable-next-line no-console
        console.debug(`API ${response.config.method.toUpperCase()} ${response.config.url} ${response.status} ${duration}ms`);
      }
    } catch (e) {}
    return response;
  },
  (error) => {
    const config = error.config || {};
    try {
      const start = config?.metadata?.startTime;
      if (start) {
        const duration = new Date() - new Date(start);
        // eslint-disable-next-line no-console
        console.warn(`API ${config.method?.toUpperCase() || ''} ${config.url || ''} error after ${duration}ms`, error.message);
      }
    } catch (e) {}
    return Promise.reject(error);
  }
);

export default api;
