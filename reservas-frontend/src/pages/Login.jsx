import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/hooks/useAuth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      alert("Credenciales inválidas");
      console.error(err);
    }
  };

  return (
    <section className="auth">
      <h2>Ingresar</h2>
      <form className="form" onSubmit={submit}>
        <label>
          Correo
          <input value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={password}
                 onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button className="btn" type="submit">Entrar</button>
      </form>
      <p className="muted">
        ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
      </p>
    </section>
  );
}
