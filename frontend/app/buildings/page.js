"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";
import { Hammer, Plus, Trash2, X } from "lucide-react";
import Toast from "../../components/Toast";
import ItemIcon from "../../components/nation/ItemIcon";
import GameProgressBar from "../../components/ui/GameProgressBar";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function ConstructionCost({ cost, resources }) {
  const t = useTranslations("Buildings");
  const resourceByCode = Object.fromEntries(resources.map((resource) => [resource.code, resource]));
  const entries = Object.entries(cost?.resources || {});
  const workerDays = cost?.worker_days || 0;
  if (entries.length === 0 && workerDays === 0) return <span className="building-cost">{t("costMissing")}</span>;
  return <div className="building-cost"><span>{t("cost")}</span>{entries.map(([code, amount]) => <span className="cost-resource" key={code}><ItemIcon item={resourceByCode[code] || { code, name: code }} type="resource" />{amount}</span>)}{workerDays > 0 && <span>{t("workerDays", {amount: workerDays})}</span>}</div>;
}

export default function Buildings() {
  const t = useTranslations();
  const dataT = useTranslations("Data");
  const [definitions, setDefinitions] = useState([]);
  const [built, setBuilt] = useState([]);
  const [resources, setResources] = useState([]);
  const [nation, setNation] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [buildingToConstruct, setBuildingToConstruct] = useState(null);
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [constructionWorkers, setConstructionWorkers] = useState(1);
  const [message, setMessage] = useState("");
  const [nationId, setNationId] = useState("");
  const assignedWorkers = processes.filter((process) => process.status === "active").reduce((total, process) => total + process.assigned_workers, 0);
  const availableWorkers = Math.max(0, (nation?.active_population || 0) - assignedWorkers);
  const resourceAmounts = Object.fromEntries((nation?.resources || []).map((resource) => [resource.code, resource.amount]));
  const availableLocations = locations.filter((location) => location.is_discovered && location.buildings.includes(buildingToConstruct?.building.code));
  const builtByType = built.reduce((groups, building) => {
    (groups[building.building_type] ||= []).push(building);
    return groups;
  }, {});
  const underConstruction = processes.filter((process) => ["active", "paused"].includes(process.status) && process.work_type === "building" && process.outputs?.building);

  async function load(id) {
    const [available, existing, resourceDefinitions, nationData, nationProcesses, locationData] = await Promise.all([
      fetch(`${API_URL}/buildings`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}/buildings`).then((response) => response.json()),
      fetch(`${API_URL}/resources`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}/processes`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}/locations`).then((response) => response.json()),
    ]);
    setDefinitions(available); setBuilt(existing); setResources(resourceDefinitions); setNation(nationData); setProcesses(nationProcesses); setLocations(locationData);
  }

  useEffect(() => { const id = window.localStorage.getItem("nationId"); if (id) { setNationId(id); load(id); } }, []);
  function build(building) {
    const costs = Object.entries(building.construction_cost?.resources || {});
    const unavailable = costs.find(([code, amount]) => (resourceAmounts[code] || 0) < amount);
    if (unavailable) return setMessage(t("Buildings.notEnoughResource", {resource: dataT(`resources.${unavailable[0]}`)}));
    if (!building.construction_cost?.worker_days) return setMessage(t("Buildings.missingWorkerDays"));
    if (!availableWorkers) return setMessage(t("Buildings.noWorkers"));
    setConstructionWorkers(1); setSelectedLocation(locations.find((location) => location.is_discovered && location.buildings.includes(building.code))?.code || ""); setBuildingToConstruct({ building, action: "build" }); setMessage("");
  }
  async function startConstruction(event) {
    event.preventDefault();
    if (Number(constructionWorkers) < 1 || Number(constructionWorkers) > availableWorkers) return setMessage(t("Buildings.workersAvailable", {amount: availableWorkers}));
    if (!selectedLocation) return;
    const response = await fetch(`${API_URL}/nations/${nationId}/buildings/${buildingToConstruct.building.code}/construction`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ location_code: selectedLocation, assigned_workers: Number(constructionWorkers) }) });
    const data = await response.json();
    if (!response.ok) return setMessage(data.detail || t("Buildings.startFailed"));
    setBuildingToConstruct(null); await load(nationId);
  }
  async function add() { if (!selectedLocation) return; const response = await fetch(`${API_URL}/nations/${nationId}/buildings/${buildingToConstruct.building.code}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ location_code: selectedLocation }) }); const data = await response.json(); if (!response.ok) return setMessage(data.detail || t("Buildings.startFailed")); setBuildingToConstruct(null); await load(nationId); }
  async function remove(buildingId) { await fetch(`${API_URL}/nations/${nationId}/buildings/${buildingId}`, { method: "DELETE" }); setSelectedBuilding(null); await load(nationId); }

  return <main><Toast message={message} setMessage={setMessage} /><header className="page-header"><div><p className="eyebrow">{t("Common.nationSimulator")}</p><h1>{t("Buildings.title")}</h1></div>{nation && <p className="page-day">{t("Common.day", {day: nation.current_day})}</p>}</header><section className="grid"><section className="card"><h2>{t("Buildings.available")}</h2>{definitions.map((building) => <div className="building" key={building.code}><strong><ItemIcon item={building} type="building" /></strong><span>{dataT(`buildingTypes.${building.building_type}`)} · {building.capacity}</span><ConstructionCost cost={building.construction_cost} resources={resources} /><div className="building-buttons"><button className="button-primary" onClick={() => build(building)}><Hammer aria-hidden="true" />{t("Buildings.build")}</button><button className="button-primary" onClick={() => { setSelectedLocation(locations.find((location) => location.is_discovered && location.buildings.includes(building.code))?.code || ""); setBuildingToConstruct({ building, action: "add" }); }}><Plus aria-hidden="true" />{t("Common.add")}</button></div></div>)}</section><section className="card"><div className="section-heading"><h2>{t("Buildings.underConstruction")}</h2>{underConstruction.length > 0 && <a className="button-secondary" href="/processes">{t("Buildings.manageProcess")}</a>}</div>{underConstruction.length === 0 ? <p>{t("Buildings.noneUnderConstruction")}</p> : underConstruction.map((process) => { const building = definitions.find((item) => item.code === process.outputs.building.code) || process.outputs.building; const remaining = Math.max(0, (process.required_worker_days || 0) - process.completed_worker_days); const days = process.assigned_workers ? Math.ceil(remaining / process.assigned_workers) : null; return <article className="construction-process" key={process.id}><ItemIcon item={building} type="building" /><div><strong>{dataT(`buildings.${building.code}`, { default: building.name })}</strong><span>{t("History.workers", { amount: process.assigned_workers })}</span><GameProgressBar value={process.completed_worker_days} max={process.required_worker_days || 1} /><span>{Math.round((process.completed_worker_days / (process.required_worker_days || 1)) * 100)}%{days !== null && ` · ${t("Processes.remaining", { days })}`}</span></div></article>; })}</section><section className="card"><h2>{t("Buildings.built")}</h2>{built.length === 0 ? <p>{t("Buildings.noneBuilt")}</p> : <div className="built-building-types">{Object.entries(builtByType).map(([type, buildings]) => <section className="building-type" key={type}><h3>{dataT(`buildingTypes.${type}`)}</h3><div className="building-icon-grid">{buildings.map((building) => <button className="button-secondary button-icon building-icon-button" type="button" key={building.id} onClick={() => setSelectedBuilding(building)} aria-label={dataT(`buildings.${building.code}`)}><ItemIcon item={building} type="building" /></button>)}</div><p>{t("Buildings.groupSummary", {type: dataT(`buildingTypes.${type}`), capacity: buildings.reduce((total, building) => total + building.capacity, 0)})}</p></section>)}</div>}</section></section>{buildingToConstruct && <div className="modal-backdrop"><form className="modal" onSubmit={buildingToConstruct.action === "build" ? startConstruction : (event) => { event.preventDefault(); add(); }}><h2>{buildingToConstruct.action === "build" ? t("Buildings.construction") : t("Common.add")}</h2>{buildingToConstruct.action === "build" && <><p>{t("Buildings.availableWorkers", {amount: availableWorkers})}</p><ConstructionCost cost={buildingToConstruct.building.construction_cost} resources={resources} /></>}<label>{t("Buildings.location")}<select value={selectedLocation} onChange={(event) => setSelectedLocation(event.target.value)} required>{availableLocations.map((location) => <option key={location.code} value={location.code}>{location.name}</option>)}</select></label>{buildingToConstruct.action === "build" && <label>{t("Buildings.workers")}<input type="number" min="1" max={availableWorkers} value={constructionWorkers} onChange={(event) => setConstructionWorkers(event.target.value)} required /></label>}<div><button className="button-secondary" type="button" onClick={() => setBuildingToConstruct(null)}>{t("Common.cancel")}</button><button className="button-primary" disabled={!selectedLocation}>{buildingToConstruct.action === "build" ? <><Hammer aria-hidden="true" />{t("Buildings.startConstruction")}</> : <><Plus aria-hidden="true" />{t("Common.add")}</>}</button></div></form></div>}{selectedBuilding && <div className="modal-backdrop"><section className="modal building-details-modal"><button className="button-secondary button-icon modal-close" type="button" onClick={() => setSelectedBuilding(null)} aria-label={t("Common.close")}><X aria-hidden="true" /></button><ItemIcon item={selectedBuilding} type="building_detail" /><h2>{dataT(`buildings.${selectedBuilding.code}`)}</h2><p>{t("Buildings.groupSummary", {type: dataT(`buildingTypes.${selectedBuilding.building_type}`), capacity: selectedBuilding.capacity})}</p><button className="button-danger remove-button" type="button" onClick={() => remove(selectedBuilding.id)}><Trash2 aria-hidden="true" />{t("Common.remove")}</button></section></div>}</main>;
}
