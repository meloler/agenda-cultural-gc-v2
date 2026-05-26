import Link from "next/link";
import { notFound } from "next/navigation";
import { EventDecisionPanel } from "../../../components/EventDecisionPanel";
import { EventDetailHero } from "../../../components/EventDetailHero";
import { EventRecommendationReasons, getRecommendationReasons } from "../../../components/EventRecommendationReasons";
import { getEventById } from "../../../lib/events/get-event-by-id";

function detailSignal(reasons: string[]): string {
  if (reasons.some((reason) => reason.includes("Ocurre hoy"))) return "Para decidir hoy";
  if (reasons.some((reason) => reason.includes("gratis") || reason.includes("Gratis"))) return "Gratis";
  if (reasons.some((reason) => reason.includes("ubicacion"))) return "Ubicación clara";
  return "Plan destacado";
}

export default async function EventDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await getEventById(decodeURIComponent(id));

  if (result.status === "not-found") {
    notFound();
  }

  if (result.status === "not-publishable") {
    return (
      <main className="detail-shell detail-shell--state">
        <Link className="back-link" href="/">← Volver a la home</Link>
        <section className="state-card">
          <p>Evento no publicable</p>
          <h1>Este plan todavía no tiene datos suficientes.</h1>
          <span>No lo mostramos como ficha válida para evitar una mala recomendación.</span>
        </section>
      </main>
    );
  }

  const reasons = getRecommendationReasons(result.event, result.context);

  return (
    <main className="detail-shell">
      <Link className="back-link" href="/">← Volver a la home</Link>
      {result.warning ? <aside className="source-banner">{result.warning}</aside> : null}
      <EventDetailHero event={result.event} signal={detailSignal(reasons)} />
      <EventDecisionPanel event={result.event} />
      <EventRecommendationReasons event={result.event} context={result.context} />
    </main>
  );
}
