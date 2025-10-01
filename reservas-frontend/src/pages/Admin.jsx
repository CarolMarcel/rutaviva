import { useEffect, useState } from "react";
import { AdminAPI, ToursAPI } from "../services/api";

export default function Admin() {
  const [tours, setTours] = useState([]);
  const [report, setReport] = useState(null);

  const [draft, setDraft] = useState({
    name: "",
    date: "",
    time: "",
    capacity: 20,
    description: "",
    active: true,
  });

  const load = async () => {
    const { data } = await ToursAPI.list();
    setTours(data.results || data);
    const rep = await AdminAPI.reports();
    setReport(rep.data);
  };

  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    await AdminAPI.toursCRUD.create(draft);
    setDraft({ name: "", date: "", time: "", capacity: 20, description: "", active: true });
    await load();
  };

  const del = async (id) => {
    if (!confirm("¿Eliminar tour?")) return;
    await AdminAPI.toursCRUD.delete(id);
    await load();
  };

  return (
    <section>
      <h2>Administración</h2>

      <div className="grid-2">
        <form className="card form" onSubmit={create}>
          <h3>Crear tour</h3>
          <label>Nombre
            <input value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} required />
          </label>
          <label>Fecha
            <input type="date" value={draft.date} onChange={(e) => setDraft({ ...draft, date: e.target.value })} required />
          </label>
          <label>Hora
            <input type="time" value={draft.time} onChange={(e) => setDraft({ ...draft, time: e.target.value })} required />
          </label>
          <label>Capacidad
            <input type="number" min={1} value={draft.capacity} onChange={(e) => setDraft({ ...draft, capacity: e.target.value })} required />
          </label>
          <label>Descripción
            <textarea value={draft.description} onChange={(e) => setDraft({ ...draft, description: e.target.value })} />
          </label>
          <label className="inline">
            <input type="checkbox" checked={draft.active} onChange={(e) => setDraft({ ...draft, active: e.target.checked })} />
            &nbsp;Activo (visible / reservable)
          </label>
          <button className="btn" type="submit">Guardar</button>
        </form>

        <div>
          <h3>Listado de tours</h3>
          <div className="list">
            {tours.map(t => (
              <article key={t.id} className="card">
                <div>
                  <strong>{t.name}</strong>
                  <div className="muted">{t.date} · {t.time} · Capacidad {t.capacity} · Reservados {t.reservedCount}</div>
                </div>
                <button className="btn btn--ghost" onClick={() => del(t.id)}>Eliminar</button>
              </article>
            ))}
          </div>

          <h3 style={{marginTop: "2rem"}}>Reportes</h3>
          <pre className="code">{JSON.stringify(report || {}, null, 2)}</pre>
        </div>
      </div>
    </section>
  );
}
