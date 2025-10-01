import { useState } from "react";

export default function ReserveModal({ open, onClose, onSubmit, maxQty = 10 }) {
  const [qty, setQty] = useState(1);
  const [guests, setGuests] = useState(0); // opcional si manejas invitados ahora o después

  if (!open) return null;

  const submit = (e) => {
    e.preventDefault();
    onSubmit({ qty: Number(qty), guests: Number(guests) });
  };

  return (
    <div className="modal__backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>Reservar cupos</h3>
        <form onSubmit={submit} className="form">
          <label>
            Cantidad:
            <input
              type="number"
              value={qty}
              min={1}
              max={maxQty}
              onChange={(e) => setQty(e.target.value)}
              required
            />
          </label>
          <label>
            Invitados (opcional):
            <input
              type="number"
              value={guests}
              min={0}
              max={maxQty}
              onChange={(e) => setGuests(e.target.value)}
            />
          </label>
          <div className="modal__actions">
            <button type="button" className="btn btn--ghost" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn">Reservar</button>
          </div>
        </form>
      </div>
    </div>
  );
}
