"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function ObjectList({ objects, empty, t }) {
  return objects.length === 0 ? <p>{empty}</p> : <ul className="objects">{objects.map((object) => <li key={object.id || object.code}><strong>{object.name}</strong><p>{object.description}</p><span>{t("workerDays", { amount: object.worker_days })} · {t("maxWorkers", { amount: object.max_workers })}</span></li>)}</ul>;
}

export default function ObjectsPage() {
  const t = useTranslations("Objects"); const router = useRouter(); const [objects, setObjects] = useState([]); const [owned, setOwned] = useState([]);
  useEffect(() => { const nationId = window.localStorage.getItem("nationId"); if (!nationId) return router.replace("/nations"); Promise.all([fetch(`${API_URL}/objects`).then((response) => response.json()), fetch(`${API_URL}/nations/${nationId}/objects`).then((response) => response.json())]).then(([available, existing]) => { setObjects(available); setOwned(existing); }); }, []);
  return <main><header className="page-header"><div><p className="eyebrow">{t("eyebrow")}</p><h1>{t("title")}</h1></div></header><section className="grid"><section className="card"><h2>{t("available")}</h2><ObjectList objects={objects} empty={t("empty")} t={t} /></section><section className="card"><h2>{t("owned")}</h2><ObjectList objects={owned} empty={t("noOwned")} t={t} /></section></section></main>;
}
