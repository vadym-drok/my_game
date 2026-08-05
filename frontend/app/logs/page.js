"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function LogHistory() {
  const t = useTranslations();
  const [logs, setLogs] = useState(null);
  const [nation, setNation] = useState(null);

  useEffect(() => {
    const nationId = window.localStorage.getItem("nationId");
    if (!nationId) return setLogs([]);
    Promise.all([
      fetch(`${API_URL}/nations/${nationId}/logs`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${nationId}`).then((response) => response.json()),
    ]).then(([data, nationData]) => { setLogs(data); setNation(nationData); });
  }, []);

  return <main>
    <header className="page-header"><div><p className="eyebrow">{t("Common.nationSimulator")}</p><h1>{t("Logs.title")}</h1></div>{nation && <p className="page-day">{t("Common.day", {day: nation.current_day})}</p>}</header>
    <section className="card event-log">
      {logs === null ? <p>{t("Common.loading")}</p> : logs.length === 0 ? <p>{t("Logs.empty")}</p> : <ul>{logs.map((log) => <li key={log.id}><span>{t("Logs.entry", {day: log.day, message: log.message})}</span><strong className={log.amount < 0 ? "log-negative" : "log-positive"}>{log.amount > 0 ? "+" : ""}{log.amount}</strong></li>)}</ul>}
    </section>
  </main>;
}
