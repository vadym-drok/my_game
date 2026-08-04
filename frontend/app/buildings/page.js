"use client";

import { useEffect, useState } from "react";
import { ICON_SIZES } from "../settings";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function ItemIcon({ item, type = "building" }) {
  const [missing, setMissing] = useState(!item.image_path);
  return <span className={`icon-tooltip tooltip icon-frame ${item.icon_frame_image_path ? "has-frame" : ""}`} style={{ "--icon-size": `${ICON_SIZES[type]}px`, "--icon-frame": `url(${item.icon_frame_image_path})` }} data-tooltip={item.name} tabIndex="0">{missing ? <span className="game-icon fallback">{item.code}</span> : <img className="game-icon" src={item.image_path} alt={item.name} onError={() => setMissing(true)} />}</span>;
}

function ConstructionCost({ cost, resources }) {
  const resourceByCode = Object.fromEntries(resources.map((resource) => [resource.code, resource]));
  const entries = Object.entries(cost?.resources || {});
  const workerDays = cost?.worker_days || 0;
  if (entries.length === 0 && workerDays === 0) return <span className="building-cost">Вартість ще не задана.</span>;
  return <div className="building-cost"><span>Вартість:</span>{entries.map(([code, amount]) => <span className="cost-resource" key={code}><ItemIcon item={resourceByCode[code] || { code, name: code }} type="resource" />{amount}</span>)}{workerDays > 0 && <span>{workerDays} людино-днів</span>}</div>;
}

export default function Buildings() {
  const [definitions, setDefinitions] = useState([]);
  const [built, setBuilt] = useState([]);
  const [resources, setResources] = useState([]);
  const [nation, setNation] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [buildingToConstruct, setBuildingToConstruct] = useState(null);
  const [constructionWorkers, setConstructionWorkers] = useState(1);
  const [message, setMessage] = useState("");
  const [nationId, setNationId] = useState("");
  const assignedWorkers = processes.filter((process) => process.status === "active").reduce((total, process) => total + process.assigned_workers, 0);
  const availableWorkers = Math.max(0, (nation?.active_population || 0) - assignedWorkers);
  const resourceAmounts = Object.fromEntries((nation?.resources || []).map((resource) => [resource.code, resource.amount]));

  async function load(id) {
    const [available, existing, resourceDefinitions, nationData, nationProcesses] = await Promise.all([
      fetch(`${API_URL}/buildings`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}/buildings`).then((response) => response.json()),
      fetch(`${API_URL}/resources`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}/processes`).then((response) => response.json()),
    ]);
    setDefinitions(available); setBuilt(existing); setResources(resourceDefinitions); setNation(nationData); setProcesses(nationProcesses);
  }

  useEffect(() => { const id = window.localStorage.getItem("nationId"); if (id) { setNationId(id); load(id); } }, []);
  function build(building) {
    const costs = Object.entries(building.construction_cost?.resources || {});
    const unavailable = costs.find(([code, amount]) => (resourceAmounts[code] || 0) < amount);
    if (unavailable) return setMessage(`Недостатньо ресурсу: ${unavailable[0]}.`);
    if (!building.construction_cost?.worker_days) return setMessage("Для будівлі не задані людино-дні.");
    if (!availableWorkers) return setMessage("Немає доступних працівників.");
    setConstructionWorkers(1); setBuildingToConstruct(building); setMessage("");
  }
  async function startConstruction(event) {
    event.preventDefault();
    if (Number(constructionWorkers) < 1 || Number(constructionWorkers) > availableWorkers) return setMessage(`Доступно працівників: ${availableWorkers}.`);
    const response = await fetch(`${API_URL}/nations/${nationId}/buildings/${buildingToConstruct.code}/construction`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ assigned_workers: Number(constructionWorkers) }) });
    const data = await response.json();
    if (!response.ok) return setMessage(data.detail || "Не вдалося розпочати будівництво.");
    setBuildingToConstruct(null); await load(nationId);
  }
  async function add(code) { await fetch(`${API_URL}/nations/${nationId}/buildings/${code}?action=add`, { method: "POST" }); await load(nationId); }
  async function remove(buildingId) { await fetch(`${API_URL}/nations/${nationId}/buildings/${buildingId}`, { method: "DELETE" }); await load(nationId); }

  return <main><header className="page-header"><div><p className="eyebrow">Nation simulator</p><h1>Buildings</h1><a className="page-link back-link" href="/">← До нації</a></div>{nation && <p className="page-day">День {nation.current_day}</p>}</header>{message && <p className="message danger">{message}</p>}<section className="grid"><section className="card"><h2>Доступні будівлі</h2>{definitions.map((building) => <div className="building" key={building.code}><strong><ItemIcon item={building} /></strong><span>{building.building_type} · {building.capacity}</span><ConstructionCost cost={building.construction_cost} resources={resources} /><div className="building-buttons"><button onClick={() => build(building)}>Build</button><button onClick={() => add(building.code)}>ADD</button></div></div>)}</section><section className="card"><h2>Побудовані будівлі</h2>{built.length === 0 ? <p>Ще нічого не побудовано.</p> : built.map((building) => <div className="building" key={building.id}><div className="building-actions"><strong><ItemIcon item={building} /></strong><button onClick={() => remove(building.id)}>Remove</button></div><span>{building.building_type} · {building.capacity}</span></div>)}</section></section>{buildingToConstruct && <div className="modal-backdrop"><form className="modal" onSubmit={startConstruction}><h2>Будівництво</h2><p>Доступно працівників: {availableWorkers}.</p><ConstructionCost cost={buildingToConstruct.construction_cost} resources={resources} /><label>Працівники<input type="number" min="1" max={availableWorkers} value={constructionWorkers} onChange={(event) => setConstructionWorkers(event.target.value)} required /></label><div><button type="button" onClick={() => setBuildingToConstruct(null)}>Скасувати</button><button>Розпочати</button></div></form></div>}</main>;
}
