"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
const workTypes = [
  "food_gathering",
  "hunting",
  "fishing",
  "woodcutting",
  "mining",
  "building",
  "investigation",
];
const resources = [["food", "Їжа"], ["wood", "Дерево"], ["stone", "Камінь"]];

export default function Home() {
  const [nationId, setNationId] = useState("");
  const [nation, setNation] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [message, setMessage] = useState("");
  const [workerError, setWorkerError] = useState("");
  const assignedWorkers = processes
    .filter((process) => process.status === "active")
    .reduce((total, process) => total + process.assigned_workers, 0);
  const availableWorkers = nation
    ? nation.active_population - assignedWorkers
    : 0;

  useEffect(() => {
    const savedId = window.localStorage.getItem("nationId");
    if (savedId) loadNation(savedId);
  }, []);

  async function request(path, options) {
    const response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  async function loadNation(id = nationId) {
    try {
      const reports = await request(`/nations/${id}/sync`, { method: "POST" });
      const data = await request(`/nations/${id}`);
      const activeProcesses = await request(`/nations/${id}/processes`);
      setNationId(String(id));
      window.localStorage.setItem("nationId", String(id));
      setNation(data);
      setProcesses(activeProcesses);
      setMessage(reports.length ? `Оновлено днів: ${reports.length}` : "");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function createNation(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const data = await request("/nations", {
        method: "POST",
        body: JSON.stringify({
          name: form.get("name"),
          population: Number(form.get("population")),
          food: Number(form.get("food")),
        }),
      });
      await loadNation(data.id);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function createProcess(event) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const mode = form.get("mode");
    const workers = Number(form.get("workers"));
    if (workers > availableWorkers) {
      setWorkerError(`Доступно лише ${availableWorkers} працівників.`);
      return;
    }
    try {
      await request(`/nations/${nationId}/processes`, {
        method: "POST",
        body: JSON.stringify({
          name: form.get("name"),
          work_type: form.get("work_type"),
          mode,
          assigned_workers: workers,
          required_worker_days:
            mode === "finite" ? Number(form.get("required_worker_days")) : null,
        }),
      });
      formElement.reset();
      setWorkerError("");
      await loadNation();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function updateProcess(id, body) {
    try {
      await request(`/processes/${id}`, { method: "PATCH", body: JSON.stringify(body) });
      await loadNation();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main>
      <header>
        <p className="eyebrow">Nation simulator</p>
        <h1>My Game</h1>
      </header>

      {message && <p className="message">{message}</p>}

      {!nation ? (
        <section className="card">
          <h2>Нова нація</h2>
          <form onSubmit={createNation}>
            <label>Назва<input name="name" required defaultValue="Нова нація" /></label>
            <label>Населення<input name="population" type="number" min="0" defaultValue="10" /></label>
            <label>Їжа<input name="food" type="number" min="0" defaultValue="30" /></label>
            <button>Створити</button>
          </form>
          <form className="load-form" onSubmit={(event) => { event.preventDefault(); loadNation(event.currentTarget.id.value); }}>
            <label>Або відкрити за ID<input name="id" type="number" min="1" required /></label>
            <button>Відкрити</button>
          </form>
        </section>
      ) : (
        <>
          <section className="card nation">
            <div><p className="eyebrow">Нація #{nation.id}</p><h2>{nation.name}</h2></div>
            <p className="start-date"><span>Старт</span>{nation.start_date}</p>
            <dl className="population">
              <div><dt>Населення</dt><dd>{nation.population}</dd></div>
              <div><dt>Активне населення</dt><dd>{nation.active_population}</dd></div>
              <div><dt>Пасивне населення</dt><dd>{nation.passive_population}</dd></div>
            </dl>
            <dl className="resources">
              <div className="resource-head"><dt>Ресурси</dt><span>Запас</span><span>− / добу</span><span>+ / добу</span></div>
              {resources.map(([resource, label]) => (
                <div className="resource-row" key={resource}>
                  <dt>{label}</dt><dd>{nation[resource]}</dd><span className="spending">−{nation.daily_resources[resource].spending}</span><span className="income">+{nation.daily_resources[resource].income}</span>
                </div>
              ))}
            </dl>
          </section>

          <section className="grid">
            <section className="card">
              <h2>Новий процес</h2>
              <form onSubmit={createProcess}>
                <label>Назва<input name="name" required placeholder="Наприклад, лісоруби" /></label>
                <label>Робота<select name="work_type">{workTypes.map((type) => <option key={type}>{type}</option>)}</select></label>
                <label>Режим<select name="mode"><option value="continuous">Постійний</option><option value="finite">Кінцевий</option></select></label>
                <label className={workerError ? "invalid" : ""}>Працівники<input name="workers" type="number" min="0" max={availableWorkers} defaultValue="0" onChange={(event) => setWorkerError(Number(event.target.value) > availableWorkers ? `Доступно лише ${availableWorkers} працівників.` : "")} /></label>
                {workerError && <p className="field-error" role="alert">{workerError}</p>}
                <label>Людино-дні для завершення<input name="required_worker_days" type="number" min="1" defaultValue="10" /></label>
                <button>Запустити</button>
              </form>
            </section>

            <section className="card">
              <h2>Процеси</h2>
              <div className="workforce">
                <div><span>Задіяно: {assignedWorkers} / {nation.active_population}</span><span>Вільно: {availableWorkers}</span></div>
                <progress value={assignedWorkers} max={nation.active_population || 1} />
              </div>
              {processes.length === 0 ? <p>Ще немає активностей.</p> : (
                <ul className="processes">
                  {processes.map((process) => (
                    <li key={process.id}>
                      <strong>{process.name}</strong>
                      <span>{process.work_type} · {process.mode} · {process.status}</span>
                      <span>{process.assigned_workers} працівників{process.mode === "finite" && ` · ${process.completed_worker_days}/${process.required_worker_days} людино-днів`}</span>
                      <div>
                        <button onClick={() => updateProcess(process.id, { assigned_workers: Math.max(0, process.assigned_workers - 1) })}>−</button>
                        <button onClick={() => updateProcess(process.id, { assigned_workers: process.assigned_workers + 1 })}>+</button>
                        <button onClick={() => updateProcess(process.id, { status: "paused" })}>Пауза</button>
                        <button onClick={() => updateProcess(process.id, { status: "cancelled" })}>Скасувати</button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </section>
        </>
      )}
    </main>
  );
}
