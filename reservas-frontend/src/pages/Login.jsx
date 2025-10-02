import { useState } from "react";
import api, { baseURL } from "../services/api";

export default function Login() {
  const [u,setU]=useState(""); const [p,setP]=useState(""); const [err,setErr]=useState("");

  const submit = async (e) => {
  e.preventDefault();
  setErr("");

  try {
    const { data: tok } = await api.post("/auth/token/", { username: u, password: p });
    localStorage.setItem("rv_token", tok.access);

    // obtener perfil para rol
    const { data: me } = await api.get("/auth/me/");
    localStorage.setItem("rv_role", me.role);

    if (me.role === "ADMIN") window.location.href = "/admin";
    else if (me.role === "STAFF") window.location.href = "/staff";
    else window.location.href = "/";
  } catch (err) {           // <-- cambia el nombre aquí
    console.error(err);
    setErr("Usuario/contraseña inválidos");
  }
};

  return (
    <div className="login">
      <h2>RutaViva – Iniciar sesión</h2>
      <form onSubmit={submit}>
        <input placeholder="usuario" value={u} onChange={e=>setU(e.target.value)} required/>
        <input placeholder="contraseña" type="password" value={p} onChange={e=>setP(e.target.value)} required/>
        <button>Ingresar</button>
      </form>
      {err && <p style={{color:'red'}}>{err}</p>}
      <small>API: {baseURL}</small>
    </div>
  );
}
