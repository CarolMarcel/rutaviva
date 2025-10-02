import { useEffect, useState } from "react";
import { ToursAPI, ReservationsAPI } from "../../services/api";

const clp = v => v.toLocaleString('es-CL',{style:'currency', currency:'CLP'});

export default function ClientDashboard(){
  const [tours,setTours]=useState([]);
  const [msg,setMsg]=useState("");

  useEffect(()=>{
    (async()=>{
      const { data } = await ToursAPI.list();
      setTours(data.slice(0,4)); // muestra 4
    })();
  },[]);

  const reservar = async (tourId)=>{
    setMsg("");
    try{
      await ReservationsAPI.create({ tour: tourId, guests: 0 });
      setMsg("Reserva creada. Espera aprobación y confirma por correo.");
    }catch(e){
      const d = e?.response?.data?.detail || "No fue posible reservar.";
      setMsg(d);
    }
  };

  return (
    <div className="wrap">
      <h2>Explorar Destinos en Chile</h2>
      <div className="grid">
        {tours.map(t=>(
          <div className="card" key={t.id}>
            <h3>{t.name}</h3>
            <p>{t.location} • {t.date} {t.time?.substring(0,5)}</p>
            <p>{t.description}</p>
            <p><b>{clp(t.price_clp)}</b></p>
            <p>Cupos: {t.available} disponibles</p>
            <button disabled={!t.available} onClick={()=>reservar(t.id)}>Reservar ahora</button>
          </div>
        ))}
      </div>
      {msg && <p>{msg}</p>}
    </div>
  );
}
