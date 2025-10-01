// src/services/api.js
import axios from "axios";

export const baseURL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// ------ AUTH: token en cada request ------
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("rv_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ------ RESPONSE: manejo 401/403 ------
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error?.response?.status;
    if (status === 401 || status === 403) {
      localStorage.removeItem("rv_token");
      // Opcional: window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ============ Helpers ============

// Auth
export const AuthAPI = {
  login: (payload) => api.post("/auth/login/", payload),
  register: (payload) => api.post("/auth/register/", payload),
  me: () => api.get("/auth/me/"),
  logout: async () => {
    localStorage.removeItem("rv_token");
    return Promise.resolve();
  },
};

// Tours/Eventos públicos
export const ToursAPI = {
  list: (params) => api.get("/tours/", { params }),
  get: (id) => api.get(`/tours/${id}/`),

  // Alias para no tocar MyReservations.jsx (usa ReservationsAPI internamente)
  myReservations: () => ReservationsAPI.listMine(),
};

// Reservas
export const ReservationsAPI = {
  create: (payload) => api.post("/reservations/", payload),
  listMine: () => api.get("/reservations/me/"),
  cancel: (id) => api.post(`/reservations/${id}/cancel/`),

  // Confirma reserva desde link de correo
  // Ajusta la ruta según tu backend: body { token } o /confirm/<token>/
  confirm: (token) => api.post("/reservations/confirm/", { token }),
};

// Admin
export const AdminAPI = {
  toursCRUD: {
    create: (payload) => api.post("/admin/tours/", payload),
    update: (id, payload) => api.put(`/admin/tours/${id}/`, payload),
    delete: (id) => api.delete(`/admin/tours/${id}/`),
  },
  reports: () => api.get("/admin/reports/"),
  blacklist: {
    list: () => api.get("/admin/blacklist/"),
    toggle: (rutOrEmail) => api.post("/admin/blacklist/toggle/", { rutOrEmail }),
  },
};

export default api;

