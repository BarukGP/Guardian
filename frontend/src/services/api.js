import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

export async function checkHealth() {
  const response = await api.get("/");
  return response.data;
}

export default api;
