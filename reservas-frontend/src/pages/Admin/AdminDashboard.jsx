import { useEffect, useState } from "react";
import { ReservationsAPI, ToursAPI } from "../../services/api";

export default function AdminDashboard(){
  const [res,setRes]=useState([]);
  const load=async()=>{
    const { data } = await ReservationsAPI.listMine(); // admin ve todas
    setRes(data);
  };
  useEffect(()=>{load();},[]);

  const act = async(id,what)=>{
    await ReservationsAPI[what](id);
    await load();
  };

  return (
    <div className="wrap">
      <h2>Panel Administrador</h2>
      <table>
        <thead><tr><th>Tour</th><th>Cliente</th><th>Estado</th><th>Acciones</th></tr></thead>
        <tbody>
          {res.map(r=>(
            <tr key={r.id}>
              <td>{r.tour_detail?.name} ({r.tour_detail?.date})</td>
              <td>{r.user?.username}</td>
              <td>{r.status}</td>
              <td>
                {r.status==='PENDING' && <>
                  <button onClick={()=>act(r.id,'approve')}>Aprobar</button>
                  <button onClick={()=>act(r.id,'reject')}>Rechazar</button>
                </>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
