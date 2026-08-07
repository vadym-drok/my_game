"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import GameIllustrationFrame from "../../components/game-art/GameIllustrationFrame";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function LocationList({ locations, empty, showWorkerDays, t }) {
  return locations.length === 0 ? <p>{empty}</p> : <ul className="locations">{locations.map((location) => <li key={location.code}><GameIllustrationFrame src={location.image_path} alt={location.name} code={location.code} ratio="16 / 9" className="location-visual" /><div><strong>{location.name}</strong><p>{location.description}</p>{showWorkerDays && <span>{t("workerDays", { amount: location.worker_days })}</span>}</div></li>)}</ul>;
}

export default function LocationsPage() {
  const t = useTranslations("Locations"); const [locations, setLocations] = useState([]);
  useEffect(() => { fetch(`${API_URL}/locations`).then((response) => response.json()).then(setLocations); }, []);
  const discovered = locations.filter((location) => location.is_discovered); const notDiscovered = locations.filter((location) => !location.is_discovered);
  return <main><header className="page-header"><div><p className="eyebrow">{t("eyebrow")}</p><h1>{t("title")}</h1></div></header><section className="grid"><section className="card"><h2>{t("discovered")}</h2><LocationList locations={discovered} empty={t("noDiscovered")} t={t} /></section><section className="card"><h2>{t("notDiscovered")}</h2><LocationList locations={notDiscovered} empty={t("noNotDiscovered")} showWorkerDays t={t} /></section></section></main>;
}
