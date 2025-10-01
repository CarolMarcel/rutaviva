import { Link } from "react-router-dom";

export default function Home() {
  return (
    <section className="hero">
      <div className="hero__overlay" />
      <div className="hero__content">
        <h1>Explora Chile con RutaViva</h1>
        <p>
          Desiertos, glaciares, bosques milenarios y ciudades patrimoniales. 
          Reserva tours verificados y recibe confirmación en tu correo.
        </p>
        <div className="hero__actions">
          <Link className="btn" to="/tours">Ver próximos tours</Link>
          <a className="btn btn--ghost" href="#como-funciona">¿Cómo funciona?</a>
        </div>
      </div>

      <div id="como-funciona" className="features">
        <article>
          <h3>Reserva segura</h3>
          <p>Disponibilidad en tiempo real y confirmación por correo con un solo clic.</p>
        </article>
        <article>
          <h3>Transparencia</h3>
          <p>Política de blacklist para cuidar la experiencia de todos. Excepciones evaluadas por admin.</p>
        </article>
        <article>
          <h3>Experiencias únicas</h3>
          <p>Agenda con eventos culturales y tours guiados por profesionales.</p>
        </article>
      </div>
    </section>
  );
}
