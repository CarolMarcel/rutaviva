import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/hooks/useAuth";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const submit = async (e) => {
    e.preventDefault();
    try {
      await register(form);
      alert("Registro exitoso. Ahora puedes iniciar sesión.");
      navigate("/login");
    } catch (err) {
      alert("No se pudo registrar. Revisa los datos.");
      console.error(err);
    }
  };

  return (
    <section className="auth">
      <h2>Crear cuenta</h2>
      <form className="form" onSubmit={submit}>
        <label>
          Nombre
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        </label>
        <label>
          Correo
          <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        </label>
        <button className="btn" type="submit">Registrarse</button>
      </form>
      <p className="muted">
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
      </p>
    </section>
  );
}
