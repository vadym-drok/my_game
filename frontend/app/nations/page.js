"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function NationsPage() {
  const t = useTranslations();
  const router = useRouter();
  const [nations, setNations] = useState(null);
  const [message, setMessage] = useState("");
  const request = async (path, options) => {
    const response = await fetch(`${API_URL}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
  };
  const openNation = (id) => { window.localStorage.setItem("nationId", String(id)); router.push("/"); };
  const loadNations = async () => { try { setNations(await request("/nations")); } catch (error) { setMessage(error.message); } };
  useEffect(() => { loadNations(); }, []);
  async function createNation(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const nation = await request("/nations", { method: "POST", body: JSON.stringify({ name: form.get("name"), population: Number(form.get("population")), resources: { general_points: Number(form.get("general_points")) } }) });
      openNation(nation.id);
    } catch (error) { setMessage(error.message); }
  }
  return <main><header><p className="eyebrow">{t("Common.nationSimulator")}</p><div className="app-title"><h1>{t("Home.title")}</h1></div></header>{message && <p className="message">{message}</p>}<section className="card"><h2>{t("Home.newNation")}</h2><form onSubmit={createNation}><label>{t("Home.name")}<input name="name" required defaultValue={t("Home.newNation")} /></label><label>{t("Home.population")}<input name="population" type="number" min="0" defaultValue="10" /></label><label>{t("Home.generalPoints")}<input name="general_points" type="number" min="0" defaultValue="30" /></label><button className="button-primary">{t("Home.create")}</button></form><div className="load-form"><h2>{t("Home.createdNations")}</h2>{nations === null ? <p>{t("Common.loading")}</p> : nations.length === 0 ? <p>{t("Home.noNations")}</p> : <ul className="nation-list">{nations.map((nation) => <li key={nation.id}><span><small>#{nation.id}</small> {nation.name} <small>({t("Common.day", { day: nation.current_day })})</small></span><button className="button-secondary" type="button" onClick={() => openNation(nation.id)}>{t("Common.open")}</button></li>)}</ul>}</div></section></main>;
}
