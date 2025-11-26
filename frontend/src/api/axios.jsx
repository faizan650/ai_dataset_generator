import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,   // Render backend URL
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
});

export default API;
