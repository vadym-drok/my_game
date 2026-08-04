"use client";

import { useEffect, useState } from "react";
import { ICON_SIZES } from "../settings";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function BuildingIcon({ building }) {
  const [missing, setMissing] = useState(!building.image_path);
  return <span className="icon-tooltip tooltip" style={{ "--icon-size": `${ICON_SIZES.building}px` }} data-tooltip={building.name} tabIndex="0">{missing ? <span className="game-icon fallback">{building.code}</span> : <img className="game-icon" src={building.image_path} alt={building.name} onError={() => setMissing(true)} />}</span>;
}

export default function Buildings() {
  const [definitions, setDefinitions] = useState([]);
  const [built, setBuilt] = useState([]);
  const [nationId, setNationId] = useState("");

  async function load(id) {
    const [available, existing] = await Promise.all([
      fetch(`${API_URL}/buildings`).then((response) => response.json()),
      fetch(`${API_URL}/nations/${id}/buildings`).then((response) => response.json()),
    ]);
    setDefinitions(available); setBuilt(existing);
  }

  useEffect(() => { const id = window.localStorage.getItem("nationId"); if (id) { setNationId(id); load(id); } }, []);
  async function build(code) { await fetch(`${API_URL}/nations/${nationId}/buildings/${code}`, { method: "POST" }); await load(nationId); }

  return <main><header><p className="eyebrow">Nation simulator</p><h1>Buildings</h1><a className="back-link" href="/">← До нації</a></header><section className="grid"><section className="card"><h2>Доступні будівлі</h2>{definitions.map((building) => <div className="building" key={building.code}><strong><BuildingIcon building={building} /></strong><span>{building.building_type} · {building.capacity}</span><button onClick={() => build(building.code)}>Build</button></div>)}</section><section className="card"><h2>Побудовані будівлі</h2>{built.length === 0 ? <p>Ще нічого не побудовано.</p> : built.map((building) => <div className="building" key={building.id}><strong><BuildingIcon building={building} /></strong><span>{building.building_type} · {building.capacity}</span></div>)}</section></section></main>;
}
