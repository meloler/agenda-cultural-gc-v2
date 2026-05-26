"use client";

import Link from "next/link";

export default function AppError({ reset }: { reset: () => void }) {
  return (
    <main className="detail-shell detail-shell--state">
      <section className="state-card">
        <p>Error controlado</p>
        <h1>No pudimos preparar los planes.</h1>
        <span>La app sigue protegida: no mostramos datos dudosos si la fuente falla.</span>
        <div className="state-actions">
          <button type="button" onClick={reset}>Intentar de nuevo</button>
          <Link href="/">Volver a la home</Link>
        </div>
      </section>
    </main>
  );
}
