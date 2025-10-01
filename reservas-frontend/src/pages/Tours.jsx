import { useEffect, useState } from "react";
import { ToursAPI } from "../services/api";
import TourCard from "../components/TourCard";

export default function Tours() {
  const [tours, setTours] = useState([]);
  const [loading, setLoading] = useState(false);
  const [q, setQ] = useState("");

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const { data } = await ToursAPI.list({ q });
        setTours(data.results || data);
      } finally {
        setLoading(false);
      }
    })();
  }, [q]);

  return (
    <section>
      <h2>Próximos Tours</h2>
      <div className="filters">
        <input
          placeholder="Buscar por nombre o fecha (YYYY-MM-DD)"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>

      {loading && <p>Cargando...</p>}
      {!loading && tours.length === 0 && <p>No hay tours disponibles.</p>}

      <div className="grid">
        {tours.map((t) => <TourCard key={t.id} tour={t} />)}
      </div>
    </section>
  );
}
