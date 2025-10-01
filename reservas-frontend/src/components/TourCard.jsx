import { Link } from "react-router-dom";

export default function TourCard({ tour }) {
  const booked = tour.reservedCount || 0;
  const capacity = tour.capacity || 0;
  const left = Math.max(0, capacity - booked);
  const active = tour.active !== false;

  return (
    <article className={`card tour ${active ? "" : "tour--inactive"}`}>
      <img
        src={tour.coverUrl || `https://images.unsplash.com/photo-1544989164-31dc3c645987?w=1200&q=60`}
        alt={tour.name}
        className="tour__img"
      />
      <div className="tour__body">
        <h3 className="tour__title">{tour.name}</h3>
        <p className="muted">{tour.date} · {tour.time} · Capacidad: {capacity}</p>
        <p className="tour__desc">{tour.description?.slice(0, 140) || "Sin descripción..."}</p>
        <div className="tour__meta">
          <span className={`pill ${left > 0 ? "pill--ok" : "pill--warn"}`}>
            {left > 0 ? `${left} cupos disponibles` : "Sin cupos"}
          </span>
          <Link to={`/tours/${tour.id}`} className="btn btn--sm">Ver detalle</Link>
        </div>
      </div>
    </article>
  );
}
