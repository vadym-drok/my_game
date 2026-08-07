"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";
import ItemIcon from "../../components/nation/ItemIcon";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
export default function History() {
  const t = useTranslations();
  const [processes, setProcesses] = useState(null);
  const [workRules, setWorkRules] = useState([]);
  const [nation, setNation] = useState(null);
  const workTypesByCode = Object.fromEntries(workRules.map((workType) => [workType.code, workType]));

  useEffect(() => {
    const nationId = window.localStorage.getItem("nationId");
    if (!nationId) return setProcesses([]);
    Promise.all([
      fetch(`${API_URL}/nations/${nationId}/processes`).then((response) => response.json()),
      fetch(`${API_URL}/work-rules`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${nationId}`).then((response) => response.json()),
    ]).then(([data, rules, nationData]) => { setProcesses(data.filter((process) => process.status !== "active")); setWorkRules(rules); setNation(nationData); });
  }, []);

  return <main>
    <header className="page-header"><div><p className="eyebrow">{t("Common.nationSimulator")}</p><h1>{t("History.title")}</h1></div>{nation && <p className="page-day">{t("Common.day", {day: nation.current_day})}</p>}</header>
    <section className="card">
      {processes === null ? <p>{t("Common.loading")}</p> : processes.length === 0 ? <p>{t("History.empty")}</p> : <ul className="processes history">
        {processes.map((process) => <li key={process.id}><strong>{process.name}</strong><span className="process-work"><ItemIcon item={workTypesByCode[process.work_type] || { code: process.work_type, name: process.work_type }} type="work_type" />{t(`Modes.${process.mode}`)} · {t(`Statuses.${process.status}`)}</span><span>{t("History.workers", {amount: process.assigned_workers})}{process.mode === "finite" && ` · ${t("History.workerDays", {completed: process.completed_worker_days, required: process.required_worker_days})}`}</span></li>)}
      </ul>}
    </section>
  </main>;
}
