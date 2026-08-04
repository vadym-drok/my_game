"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function LogHistory() {
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
    <header className="page-header"><div><p className="eyebrow">Nation simulator</p><h1>Історія подій</h1><a className="back-link" href="/">← До нації</a></div>{nation && <p className="page-day">День {nation.current_day}</p>}</header>
    <section className="card event-log">
      {logs === null ? <p>Завантаження…</p> : logs.length === 0 ? <p>Подій поки немає.</p> : <ul>{logs.map((log) => <li key={log.id}><span>День {log.day} · {log.message}</span><strong className={log.amount < 0 ? "log-negative" : "log-positive"}>{log.amount > 0 ? "+" : ""}{log.amount}</strong></li>)}</ul>}
    </section>
  </main>;
}
