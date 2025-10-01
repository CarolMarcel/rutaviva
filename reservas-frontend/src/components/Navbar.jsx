import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
  try {
    await logout();
  } catch (err) {
    console.error("Error cerrando sesión:", err);
  } finally {
    navigate("/");
  }
};

  return (
    <header className="nav">
      <div className="nav__inner">
        <Link to="/" className="brand" aria-label="RutaViva - Inicio">
          <img 
            src="/logo-rutaviva.svg" 
            alt="RutaViva" 
            className="brand__logo" 
            //eight={62} 
          />
        </Link>

        <nav className="nav__links">
          <NavLink to="/" end>Inicio</NavLink>
          <NavLink to="/tours" className={({ isActive }) => (isActive ? "active" : "")}> Tours </NavLink>
          {user && <NavLink to="/reservas">Mis reservas</NavLink>}
          {user?.role === "admin" && <NavLink to="/admin">Administración</NavLink>}
        </nav>

        <div className="nav__auth">
          {user ? (
            <>
              <span className="nav__user">Hola, {user.name || user.email}</span>
              <button className="btn btn--ghost" onClick={handleLogout}>Salir</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn--ghost">Ingresar</Link>
              <Link to="/register" className="btn">Registrarse</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
