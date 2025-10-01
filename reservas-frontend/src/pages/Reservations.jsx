import { useEffect, useState } from "react";
import { ReservationsAPI } from "../services/api";

export default function Reservations() {
  const [list, setList] = useState([]);

  const load = async () => {
    const { data } = await ReservationsAPI.listMine();
    setList(data.results || data);
  };

  useEffect(() => { load(); }, []);

  const cancel = async (id) => {
    if (!confirm("¿Cancelar esta reserva?")) return;
    await ReservationsAPI.cancel(id);
    await load();
  };

  return (
    <section>
      <h2>Mis reservas</h2>
      {list.length === 0 && <p className="muted">Aún no tienes reservas.</p>}

      <div className="list">
        {list.map((r) => (
          <article key={r.id} className="card">
            <div>
              <strong>{r.event?.name}</strong>
              <div className="muted">
                {r.qty} cupos · Estado: <b>{r.status}</b>
              </div>
            </div>
            {r.status !== "cancelled" && (
              <button className="btn btn--ghost" onClick={() => cancel(r.id)}>Cancelar</button>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
