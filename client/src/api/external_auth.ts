import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sanvia-refreshToken");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  // console.log(`Token value: ${token}`);
  // console.log('Request Headers Before Sending:', config.headers);
  return config;
});

export const whoopapi = {
  connectWhoop: async () => {
    try {
      const response = await api.get("/auth/whoop/redirect"); // Call your backend
      const whoopRedirectUrl = response.data.url; // You must return this from backend
      window.location.href = whoopRedirectUrl; // Redirect browser to WHOOP directly
    } catch (error) {
      console.error("Error during WHOOP redirect:", error);
    }
  },
};

export default whoopapi;
