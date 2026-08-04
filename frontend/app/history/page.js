"use client";

import { useEffect, useState } from "react";
import { ICON_SIZES } from "../settings";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
const statusLabels = { stopped: "зупинено", completed: "завершено", paused: "призупинено", cancelled: "зупинено" };

function ItemIcon({ item, type = "resource" }) {
  const [missing, setMissing] = useState(!item.image_path);
  return <span className={`icon-tooltip tooltip icon-frame ${item.icon_frame_image_path ? "has-frame" : ""}`} style={{ "--icon-size": `${ICON_SIZES[type]}px`, "--icon-frame": `url(${item.icon_frame_image_path})` }} data-tooltip={item.name} tabIndex="0">{missing ? <span className="game-icon fallback">{item.code}</span> : <img className="game-icon" src={item.image_path} alt={item.name} onError={() => setMissing(true)} />}</span>;
}

export default function History() {
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
    <header className="page-header"><div><p className="eyebrow">Nation simulator</p><h1>Історія процесів</h1><a className="back-link" href="/">← До нації</a></div>{nation && <p className="page-day">День {nation.current_day}</p>}</header>
    <section className="card">
      {processes === null ? <p>Завантаження…</p> : processes.length === 0 ? <p>Історія поки порожня.</p> : <ul className="processes history">
        {processes.map((process) => <li key={process.id}><strong>{process.name}</strong><span className="process-work"><ItemIcon item={workTypesByCode[process.work_type] || { code: process.work_type, name: process.work_type }} type="work_type" />{process.mode} · {statusLabels[process.status] || process.status}</span><span>{process.assigned_workers} працівників{process.mode === "finite" && ` · ${process.completed_worker_days}/${process.required_worker_days} людино-днів`}</span></li>)}
      </ul>}
    </section>
  </main>;
}
