import axios from "axios";

const api = axios.create({
   baseURL: "/api",
});

export async function checkHealth() {
  const response = await api.get("/");
  return response.data;
}