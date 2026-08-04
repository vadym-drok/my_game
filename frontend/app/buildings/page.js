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
  const [nationId, setNationId] = useState("");

  async function load(id) {
    const [available, existing, resourceDefinitions] = await Promise.all([
      fetch(`${API_URL}/buildings`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}/buildings`).then((response) => response.json()),
      fetch(`${API_URL}/resources`).then((response) => response.json()),
    ]);
    setDefinitions(available); setBuilt(existing); setResources(resourceDefinitions);
  }

  useEffect(() => { const id = window.localStorage.getItem("nationId"); if (id) { setNationId(id); load(id); } }, []);
  async function build(code) { await fetch(`${API_URL}/nations/${nationId}/buildings/${code}`, { method: "POST" }); await load(nationId); }
  async function add(code) { await fetch(`${API_URL}/nations/${nationId}/buildings/${code}?action=add`, { method: "POST" }); await load(nationId); }
  async function remove(buildingId) { await fetch(`${API_URL}/nations/${nationId}/buildings/${buildingId}`, { method: "DELETE" }); await load(nationId); }

  return <main><header><p className="eyebrow">Nation simulator</p><h1>Buildings</h1><a className="back-link" href="/">← До нації</a></header><section className="grid"><section className="card"><h2>Доступні будівлі</h2>{definitions.map((building) => <div className="building" key={building.code}><strong><ItemIcon item={building} /></strong><span>{building.building_type} · {building.capacity}</span><ConstructionCost cost={building.construction_cost} resources={resources} /><div className="building-buttons"><button onClick={() => build(building.code)}>Build</button><button onClick={() => add(building.code)}>ADD</button></div></div>)}</section><section className="card"><h2>Побудовані будівлі</h2>{built.length === 0 ? <p>Ще нічого не побудовано.</p> : built.map((building) => <div className="building" key={building.id}><div className="building-actions"><strong><ItemIcon item={building} /></strong><button onClick={() => remove(building.id)}>Remove</button></div><span>{building.building_type} · {building.capacity}</span></div>)}</section></section></main>;
}
