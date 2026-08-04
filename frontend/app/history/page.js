"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
const statusLabels = { stopped: "зупинено", completed: "завершено", paused: "призупинено", cancelled: "зупинено" };

export default function History() {
  const [processes, setProcesses] = useState(null);

  useEffect(() => {
    const nationId = window.localStorage.getItem("nationId");
    if (!nationId) return setProcesses([]);
    fetch(`${API_URL}/nations/${nationId}/processes`)
      .then((response) => response.json())
      .then((data) => setProcesses(data.filter((process) => process.status !== "active")));
  }, []);

  return <main>
    <header><p className="eyebrow">Nation simulator</p><h1>Історія процесів</h1><a className="back-link" href="/">← До нації</a></header>
    <section className="card">
      {processes === null ? <p>Завантаження…</p> : processes.length === 0 ? <p>Історія поки порожня.</p> : <ul className="processes history">
        {processes.map((process) => <li key={process.id}><strong>{process.name}</strong><span>{process.work_type} · {process.mode} · {statusLabels[process.status] || process.status}</span><span>{process.assigned_workers} працівників{process.mode === "finite" && ` · ${process.completed_worker_days}/${process.required_worker_days} людино-днів`}</span></li>)}
      </ul>}
    </section>
  </main>;
}
