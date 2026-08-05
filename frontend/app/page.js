"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";
import { ICON_SIZES } from "./settings";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
const intensityCoefficients = { BASE: 1, LIGHT: 1.5, STANDARD: 2, MEDIUM: 2.5, HEAVY: 3 };
function ItemIcon({ item, type = "resource" }) {
  const t = useTranslations("Data");
  const [missing, setMissing] = useState(!item.image_path);
  const category = type === "work_type" ? "workTypes" : "resources";
  const name = t(`${category}.${item.code}`, {default: item.name || item.code});
  return <span className={`icon-tooltip tooltip icon-frame ${item.icon_frame_image_path ? "has-frame" : ""}`} style={{ "--icon-size": `${ICON_SIZES[type]}px`, "--icon-frame": `url(${item.icon_frame_image_path})` }} data-tooltip={name} tabIndex="0">{missing ? <span className="game-icon fallback">{item.code}</span> : <img className="game-icon" src={item.image_path} alt={name} onError={() => setMissing(true)} />}</span>;
}

export default function Home() {
  const t = useTranslations();
  const dataT = useTranslations("Data");
  const [nationId, setNationId] = useState("");
  const [nation, setNation] = useState(null);
  const [nations, setNations] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [logs, setLogs] = useState([]);
  const [workRules, setWorkRules] = useState([]);
  const [workInfoOpen, setWorkInfoOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [workerError, setWorkerError] = useState("");
  const [growthModalOpen, setGrowthModalOpen] = useState(false);
  const [growthAmount, setGrowthAmount] = useState(0);
  const [spendModalOpen, setSpendModalOpen] = useState(false);
  const [purchaseAmounts, setPurchaseAmounts] = useState({});
  const [resourceAmounts, setResourceAmounts] = useState({});
  const [selectedWorkType, setSelectedWorkType] = useState("food_gathering");
  const assignedWorkers = processes
    .filter((process) => process.status === "active")
    .reduce((total, process) => total + process.assigned_workers, 0);
  const availableWorkers = nation
    ? nation.active_population - assignedWorkers
    : 0;
  const currentProcesses = processes.filter((process) => process.status === "active");
  const resourceNames = Object.fromEntries((nation?.resources || []).map((resource) => [resource.code, dataT(`resources.${resource.code}`, {default: resource.name})]));
  const workTypesByCode = Object.fromEntries(workRules.map((workType) => [workType.code, workType]));
  const generalPoints = nation?.resources?.find((resource) => resource.code === "general_points");
  const regularResources = (nation?.resources || []).filter((resource) => resource.code !== "general_points");
  const purchaseTotal = regularResources.reduce((total, resource) => total + (Number(purchaseAmounts[resource.code]) || 0), 0);
  const housingProvided = nation?.housing_capacity ?? 0;
  const housingSufficient = housingProvided >= (nation?.population ?? 0);
  const populationGrowthLimit = Math.min(nation?.population_growth.max_increase ?? 0, Math.max(0, housingProvided - (nation?.population ?? 0)));
  const storageUsed = nation?.storage?.used ?? 0;
  const storageCapacity = nation?.storage?.capacity ?? 0;
  const storageSufficient = storageCapacity >= storageUsed;
  const processMode = workRules.find((workType) => workType.code === selectedWorkType)?.mode || "continuous";
  const growthButtonText = nation?.hunger.active
    ? t("Home.hunger", {days: nation.hunger.days, stageDays: nation.hunger.stage_days})
    : nation?.population_growth.available
      ? t("Home.growth", {amount: populationGrowthLimit})
      : t("Home.untilGrowth", {days: nation?.population_growth.required_days - nation?.population_growth.progress_days});

  useEffect(() => {
    const savedId = window.localStorage.getItem("nationId");
    if (savedId) loadNation(savedId, true);
    else loadNations();
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

  async function loadNation(id = nationId, reloadTick = false) {
    try {
      const reports = await request(`/nations/${id}/sync?reload_tick=${reloadTick}`, { method: "POST" });
      const data = await request(`/nations/${id}`);
      const activeProcesses = await request(`/nations/${id}/processes`);
      const eventLogs = await request(`/nations/${id}/logs`);
      const rules = await request("/work-rules");
      setNationId(String(id));
      window.localStorage.setItem("nationId", String(id));
      setNation(data);
      setProcesses(activeProcesses);
      setLogs(eventLogs);
      setWorkRules(rules);
      const populationLoss = reports.flatMap((report) => report.notes).find((note) => note.startsWith("Population loss: "));
      setMessage(populationLoss ? t("System.populationLoss", {amount: populationLoss.split(": ")[1]}) : reports.length ? t("System.updatedDays", {days: reports.length}) : "");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadNations() {
    try {
      setNations(await request("/nations"));
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
          resources: { general_points: Number(form.get("general_points")) },
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
    const mode = processMode;
    const workers = Number(form.get("workers"));
    if (workers > availableWorkers) {
      setWorkerError(t("Home.availableWorkers", {amount: availableWorkers}));
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

  async function applyPopulationGrowth(event) {
    event.preventDefault();
    try {
      await request(`/nations/${nationId}/population-growth`, {
        method: "POST",
        body: JSON.stringify({ amount: Number(growthAmount) }),
      });
      setGrowthModalOpen(false);
      setGrowthAmount(0);
      await loadNation();
    } catch (error) {
      setMessage(error.message);
    }
  }

  function openPopulationGrowth() {
    if (!housingSufficient || populationGrowthLimit < 1) return setMessage(t("Home.housingRequired"));
    setGrowthModalOpen(true);
  }

  function openNationSelector() {
    window.localStorage.removeItem("nationId");
    window.location.href = "/";
  }

  async function adjustResource(resource) {
    const amount = Number(resourceAmounts[resource]);
    if (!Number.isInteger(amount)) {
      setMessage(t("Home.integerRequired"));
      return;
    }
    try {
      await request(`/nations/${nationId}/resources/${resource}`, {
        method: "POST",
        body: JSON.stringify({ amount }),
      });
      setResourceAmounts({ ...resourceAmounts, [resource]: "" });
      await loadNation();
    } catch (error) {
      setMessage(error.message);
    }
  }

  function openSpend() {
    setPurchaseAmounts({});
    setSpendModalOpen(true);
  }

  async function purchaseResources(event) {
    event.preventDefault();
    if (!purchaseTotal) return setMessage(t("Spend.nothing"));
    try {
      await request(`/nations/${nationId}/resource-purchases`, {
        method: "POST",
        body: JSON.stringify({resources: purchaseAmounts}),
      });
      setSpendModalOpen(false);
      await loadNation();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main>
      <header>
        <p className="eyebrow">{t("Common.nationSimulator")}</p>
        <div className="app-title"><h1>{t("Home.title")}</h1>{nation && <button className="page-link" type="button" onClick={openNationSelector}>{t("Nav.nations")}</button>}</div>
      </header>

      {message && <p className="message">{message}</p>}

      {!nation ? (
        <section className="card">
          <h2>{t("Home.newNation")}</h2>
          <form onSubmit={createNation}>
            <label>{t("Home.name")}<input name="name" required defaultValue={t("Home.newNation")} /></label>
            <label>{t("Home.population")}<input name="population" type="number" min="0" defaultValue="10" /></label>
            <label>{t("Home.generalPoints")}<input name="general_points" type="number" min="0" defaultValue="30" /></label>
            <button>{t("Home.create")}</button>
          </form>
          <div className="load-form"><h2>{t("Home.createdNations")}</h2>{nations === null ? <p>{t("Common.loading")}</p> : nations.length === 0 ? <p>{t("Home.noNations")}</p> : <ul className="nation-list">{nations.map((item) => <li key={item.id}><span><small>#{item.id}</small> {item.name} <small>({t("Common.day", {day: item.current_day})})</small></span><button className="page-link" type="button" onClick={() => loadNation(item.id)}>{t("Common.open")}</button></li>)}</ul>}</div>
        </section>
      ) : (
        <>
          <section className="card nation">
            <div><p className="eyebrow">{t("Home.nationNumber", {id: nation.id})}</p><h2>{nation.name}</h2><button className={`growth-button ${nation.hunger.active ? "hunger" : ""}`} disabled={!nation.population_growth.available} onClick={openPopulationGrowth}>{growthButtonText}</button><a className="page-link buildings-link" href="/buildings">{t("Nav.buildings")}</a></div>
            <p className="start-date"><span>{t("Common.day", {day: nation.current_day})}</span></p>
            <dl className="population">
              <div><dt>{t("Home.population")}</dt><dd className="tooltip" data-tooltip={t("Home.populationHousingHint")} tabIndex="0">{nation.population} <span className={`housing-capacity ${housingSufficient ? "sufficient" : "insufficient"}`}>({housingProvided})</span></dd></div>
              <div><dt>{t("Home.activePopulation")}</dt><dd>{nation.active_population}</dd></div>
              <div><dt>{t("Home.passivePopulation")}</dt><dd>{nation.passive_population}</dd></div>
            </dl>
            {generalPoints && <dl className="general-points">
              <div><dt><ItemIcon item={generalPoints} /></dt><dd>{generalPoints.amount}</dd></div>
              <div className="resource-adjust"><input aria-label={`${t("Home.change")} ${resourceNames[generalPoints.code]}`} type="number" step="1" value={resourceAmounts[generalPoints.code] ?? ""} onChange={(event) => setResourceAmounts({ ...resourceAmounts, [generalPoints.code]: event.target.value })} /><button type="button" onClick={() => adjustResource(generalPoints.code)}>{t("Common.add")}</button><button type="button" onClick={openSpend}>{t("Spend.button")}</button></div>
            </dl>}
            <dl className="resources">
              <div className="resource-head"><dt>{t("Home.resources")} <span className={`storage-capacity tooltip ${storageSufficient ? "sufficient" : "insufficient"}`} data-tooltip={t("Home.storageHint")} tabIndex="0">({storageUsed} / {storageCapacity})</span></dt><span>{t("Home.stock")}</span><span>{t("Home.perDaySpending")}</span><span>{t("Home.perDayIncome")}</span><span>{t("Home.change")}</span></div>
              {regularResources.map((resource) => (
                <div className="resource-row" key={resource.code}>
                  <dt><ItemIcon item={resource} /></dt><dd className={resource.code === "food" && nation.consecutive_hunger_days ? "resource-alert" : ""}>{resource.amount}</dd><span className="spending">−{resource.spending}</span><span className="income">+{resource.income}</span><div className="resource-adjust"><input aria-label={`${t("Home.change")} ${resourceNames[resource.code]}`} type="number" step="1" value={resourceAmounts[resource.code] ?? ""} onChange={(event) => setResourceAmounts({ ...resourceAmounts, [resource.code]: event.target.value })} /><button type="button" onClick={() => adjustResource(resource.code)}>{t("Common.add")}</button></div>
                </div>
              ))}
            </dl>
          </section>

          <section className="grid">
            <section className="card">
              <h2>{t("Home.newProcess")}</h2>
              <form onSubmit={createProcess}>
                <label>{t("Home.name")}<input name="name" required placeholder={t("Home.exampleProcess")} /></label>
                <label>{t("Home.work")}<select name="work_type" value={selectedWorkType} onChange={(event) => setSelectedWorkType(event.target.value)}>{workRules.map((type) => <option key={type.code} value={type.code}>{dataT(`workTypes.${type.code}`, {default: type.name})}</option>)}</select></label>
                <button className="work-info-button" type="button" aria-label={t("Home.workEffects")} title={t("Home.workEffects")} onClick={() => setWorkInfoOpen(!workInfoOpen)}>ⓘ</button>
                {workInfoOpen && <ul className="work-rules">
                  {workRules.map((rule) => <li key={rule.code}><strong><ItemIcon item={rule} type="work_type" /></strong><span className="log-negative">{t("Home.foodIntensity", {value: intensityCoefficients[rule.intensity]})}</span>{Object.entries(rule.outputs).map(([resource, amount]) => <span className="log-positive" key={resource}>+{amount} {resourceNames[resource] || resource}</span>)}</li>)}
                </ul>}
                <p>{t("Home.mode", {mode: t(`Modes.${processMode}`)})}</p>
                <label className={workerError ? "invalid" : ""}>{t("Home.workers")}<input name="workers" type="number" min="0" max={availableWorkers} defaultValue="0" onChange={(event) => setWorkerError(Number(event.target.value) > availableWorkers ? t("Home.availableWorkers", {amount: availableWorkers}) : "")} /></label>
                {workerError && <p className="field-error" role="alert">{workerError}</p>}
                {processMode === "finite" && <label>{t("Home.workerDays")}<input name="required_worker_days" type="number" min="1" defaultValue="10" required /></label>}
                <button>{t("Home.start")}</button>
              </form>
            </section>

            <div className="process-panels">
              <section className="card">
              <div className="section-heading"><h2>{t("Home.currentProcesses")}</h2><a className="page-link" href="/history">{t("Nav.history")}</a></div>
              <div className="workforce">
                <div><span>{t("Home.assigned", {assigned: assignedWorkers, total: nation.active_population})}</span></div>
                <progress value={assignedWorkers} max={nation.active_population || 1} />
              </div>
              {currentProcesses.length === 0 ? <p>{t("Home.noActiveProcesses")}</p> : (
                <ul className="processes">
                  {currentProcesses.map((process) => (
                    <li key={process.id}>
                      <strong>{process.name}</strong>
                      <span className="process-work"><ItemIcon item={workTypesByCode[process.work_type] || { code: process.work_type, name: process.work_type }} type="work_type" />{t(`Modes.${process.mode}`)}</span>
                      <span>{t("History.workers", {amount: process.assigned_workers})}{process.mode === "finite" && ` · ${t("History.workerDays", {completed: process.completed_worker_days, required: process.required_worker_days})}`}</span>
                      <div>
                        <button onClick={() => updateProcess(process.id, { assigned_workers: Math.max(0, process.assigned_workers - 1) })}>−</button>
                        <button onClick={() => updateProcess(process.id, { assigned_workers: process.assigned_workers + 1 })}>+</button>
                        <button onClick={() => updateProcess(process.id, { status: "stopped" })}>{t("Home.stop")}</button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
            </div>
            <section className="card event-log">
              <h2>{t("Home.eventHistory")}</h2>
              {logs.length === 0 ? <p>{t("Home.noEvents")}</p> : <ul>
                {logs.slice(0, 5).map((log) => <li key={log.id}><span>{t("Logs.entry", {day: log.day, message: log.message})}</span><strong className={log.amount < 0 ? "log-negative" : "log-positive"}>{log.amount > 0 ? "+" : ""}{log.amount}</strong></li>)}
              </ul>}
              <a className="page-link log-history-link" href="/logs">{t("Nav.logHistory")}</a>
            </section>
          </section>

          {growthModalOpen && <div className="modal-backdrop">
            <form className="modal" onSubmit={applyPopulationGrowth}>
              <h2>{t("Home.growthTitle")}</h2>
              <p>{t("Home.availableUpTo", {amount: populationGrowthLimit})}</p>
              <label>{t("Home.addPopulation")}<input type="number" min="0" max={populationGrowthLimit} value={growthAmount} onChange={(event) => setGrowthAmount(event.target.value)} /></label>
              <div><button type="button" onClick={() => setGrowthModalOpen(false)}>{t("Common.cancel")}</button><button>{t("Common.confirm")}</button></div>
            </form>
          </div>}
          {spendModalOpen && <div className="modal-backdrop">
            <form className="modal" onSubmit={purchaseResources}>
              <h2>{t("Spend.title")}</h2>
              <p>{t("Spend.available", {amount: generalPoints.amount})}</p>
              <p>{t("Spend.total", {amount: purchaseTotal})}</p>
              <div className="purchase-list">{regularResources.map((resource) => <label key={resource.code}><ItemIcon item={resource} />{t("Spend.amount", {resource: resourceNames[resource.code]})}<input type="number" min="0" step="1" value={purchaseAmounts[resource.code] ?? ""} onChange={(event) => setPurchaseAmounts({...purchaseAmounts, [resource.code]: event.target.value})} /></label>)}</div>
              <div><button type="button" onClick={() => setSpendModalOpen(false)}>{t("Common.cancel")}</button><button>{t("Spend.confirm")}</button></div>
            </form>
          </div>}
        </>
      )}
    </main>
  );
}
