import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ToursAPI, ReservationsAPI } from "../services/api";
import ReserveModal from "../components/ReserveModal";

export default function TourDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [tour, setTour] = useState(null);
  const [open, setOpen] = useState(false);
  const capacityLeft = Math.max(0, (tour?.capacity || 0) - (tour?.reservedCount || 0));

  useEffect(() => {
    (async () => {
      const { data } = await ToursAPI.get(id);
      setTour(data);
    })();
  }, [id]);

  const doReserve = async ({ qty }) => {
    await ReservationsAPI.create({ eventId: Number(id), qty });
    alert("Reserva creada. Revisa tu correo para confirmar.");
    setOpen(false);
  };

  if (!tour) return <p>Cargando...</p>;

  return (
    <section className="tour-detail">
      <img
        src={tour.coverUrl || `https://images.unsplash.com/photo-1526057565006-20beab9e9d22?w=1600&q=60`}
        alt={tour.name}
        className="tour-detail__img"
      />
      <div className="tour-detail__body">
        <h2>{tour.name}</h2>
        <p className="muted">{tour.date} · {tour.time}</p>
        <p>{tour.description || "Sin descripción."}</p>

        <div className="tour-detail__meta">
          <span className={`pill ${capacityLeft > 0 ? "pill--ok" : "pill--warn"}`}>
            {capacityLeft > 0 ? `${capacityLeft} cupos disponibles` : "Sin cupos"}
          </span>
          {user ? (
            <button
              className="btn"
              disabled={capacityLeft === 0 || tour.active === false}
              onClick={() => setOpen(true)}
            >
              Reservar
            </button>
          ) : (
            <p className="muted">Inicia sesión para reservar.</p>
          )}
        </div>
      </div>

      <ReserveModal
        open={open}
        onClose={() => setOpen(false)}
        onSubmit={doReserve}
        maxQty={capacityLeft || 10}
      />
    </section>
  );
}
