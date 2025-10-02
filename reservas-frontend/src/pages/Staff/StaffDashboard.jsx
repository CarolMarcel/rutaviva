import { useEffect, useState } from "react";
import { ReservationsAPI } from "../../services/api";

export default function StaffDashboard(){
  const [res,setRes]=useState([]);
  useEffect(()=>{(async()=>{ const {data}=await ReservationsAPI.listMine(); setRes(data); })();},[]);
  return (
    <div className="wrap">
      <h2>Panel Colaborador</h2>
      <p>Visualiza reservas (lectura). Acciones avanzadas quedan para Admin.</p>
      <ul>
        {res.map(r=><li key={r.id}>{r.tour_detail?.name} — {r.user?.username} — {r.status}</li>)}
      </ul>
    </div>
  );
}
