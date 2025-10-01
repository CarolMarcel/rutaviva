export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <p>© {new Date().getFullYear()} RutaViva SpA · Turismo en Chile</p>
        <p className="muted">Hecho con Django + React · Proyecto académico</p>
      </div>
    </footer>
  );
}
