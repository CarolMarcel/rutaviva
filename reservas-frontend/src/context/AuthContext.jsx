// src/context/AuthContext.jsx
import { createContext, useEffect, useState } from "react";
import { AuthAPI } from "../services/api";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Estado de autenticación
  const [user, setUser] = useState(null);      // { id, email, role, name }
  const [loading, setLoading] = useState(true);

  // Al montar: intentar recuperar sesión desde el token
  useEffect(() => {
    const tryMe = async () => {
      const token = localStorage.getItem("rv_token");
      if (!token) {
        setLoading(false);
        //return;
      }
      try {
        const { data } = await AuthAPI.me();
        setUser(data);
      } catch (err) {
        console.error("Error recuperando sesión:", err);
        localStorage.removeItem("rv_token");
      } finally {
        setLoading(false);
      }
    };
    tryMe();
  }, []);

  // --- ACCIONES ---

  const login = async (email, password) => {
    const { data } = await AuthAPI.login({ email, password });
      // Guarda el access token (si tu API devuelve refresh, puedes guardarlo aparte)
      localStorage.setItem("rv_token", data.access);

      const me = await AuthAPI.me();
      setUser(me.data);
    }
  

  const register = async (payload) => {
    await AuthAPI.register(payload);
      // El login se hace aparte (flujo explícito)
  };

  const logout = async () => {
    try {
      // Si tienes endpoint de logout, puedes llamarlo:
      // await AuthAPI.logout();
    } finally {
      localStorage.removeItem("rv_token");
      setUser(null);
    }
  };

  // Helpers para la UI
  const isAuthenticated = !!user;
  const isAdmin = user?.role === "admin";
  const isClient = user?.role === "client" || user?.role === "cliente";

  const value = {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    isClient,
    login,
    register,
    logout,
    setUser, // opcional
  };

  // OJO: los métodos deben definirse ANTES del return
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};




