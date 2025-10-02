import { useState } from "react";
import api from "../services/api"; // tu instancia de axios
import "../styles/login.css"; // opcional para estilos

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!username || !password) {
      setError("Debes completar ambos campos.");
      return;
    }

    try {
      // pedir token
      const { data: tok } = await api.post("/auth/token/", {
        username,
        password,
      });
      localStorage.setItem("rv_token", tok.access);

      // pedir perfil para rol
      const { data: me } = await api.get("/auth/me/");
      localStorage.setItem("rv_role", me.role);

      if (me.role === "ADMIN") window.location.href = "/admin";
      else if (me.role === "STAFF") window.location.href = "/staff";
      else window.location.href = "/";
    } catch (e) {
      console.error(e); // opcional: log para debug
      setError("Usuario o contraseña inválidos.");
      }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>RutaViva</h2>
        <p>Inicia sesión para continuar</p>

        {error && <div className="error">{error}</div>}

        <input
          type="text"
          placeholder="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Ingresar</button>
      </form>
    </div>
  );
}
