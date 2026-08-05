"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";
import { useRouter } from "next/navigation";
import ItemIcon from "../components/nation/ItemIcon";
import NationHeader from "../components/nation/NationHeader";
import PopulationSummary from "../components/nation/PopulationSummary";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
export default function Home() {
  const t = useTranslations();
  const dataT = useTranslations("Data");
  const router = useRouter();
  const [nationId, setNationId] = useState("");
  const [nation, setNation] = useState(null);
  const [logs, setLogs] = useState([]);
  const [message, setMessage] = useState("");
  const [growthModalOpen, setGrowthModalOpen] = useState(false);
  const [growthAmount, setGrowthAmount] = useState(0);
  const [spendModalOpen, setSpendModalOpen] = useState(false);
  const [manualAdjustmentOpen, setManualAdjustmentOpen] = useState(false);
  const [purchaseAmounts, setPurchaseAmounts] = useState({});
  const [resourceAmounts, setResourceAmounts] = useState({});
  const resourceNames = Object.fromEntries((nation?.resources || []).map((resource) => [resource.code, dataT(`resources.${resource.code}`, {default: resource.name})]));
  const generalPoints = nation?.resources?.find((resource) => resource.code === "general_points");
  const regularResources = (nation?.resources || []).filter((resource) => resource.code !== "general_points");
  const purchaseTotal = regularResources.reduce((total, resource) => total + (Number(purchaseAmounts[resource.code]) || 0), 0);
  const housingProvided = nation?.housing_capacity ?? 0;
  const housingSufficient = housingProvided >= (nation?.population ?? 0);
  const populationGrowthLimit = Math.min(nation?.population_growth.max_increase ?? 0, Math.max(0, housingProvided - (nation?.population ?? 0)));
  const storageUsed = nation?.storage?.used ?? 0;
  const storageCapacity = nation?.storage?.capacity ?? 0;
  const storageSufficient = storageCapacity >= storageUsed;
  const growthButtonText = nation?.hunger.active
    ? t("Home.hunger", {days: nation.hunger.days, stageDays: nation.hunger.stage_days})
    : nation?.population_growth.available
      ? t("Home.growth", {amount: populationGrowthLimit})
      : t("Home.untilGrowth", {days: nation?.population_growth.required_days - nation?.population_growth.progress_days});

  useEffect(() => {
    const savedId = window.localStorage.getItem("nationId");
    if (savedId) loadNation(savedId, true);
    else router.replace("/nations");
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
      const eventLogs = await request(`/nations/${id}/logs`);
      setNationId(String(id));
      window.localStorage.setItem("nationId", String(id));
      setNation(data);
      setLogs(eventLogs);
      const populationLoss = reports.flatMap((report) => report.notes).find((note) => note.startsWith("Population loss: "));
      setMessage(populationLoss ? t("System.populationLoss", {amount: populationLoss.split(": ")[1]}) : reports.length ? t("System.updatedDays", {days: reports.length}) : "");
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
        <div className="app-title"><h1>{t("Home.title")}</h1></div>
      </header>

      {message && <p className="message">{message}</p>}

      {!nation ? <p>{t("Common.loading")}</p> : (
        <>
          <section className="card nation">
            <NationHeader nation={nation} growthButtonText={growthButtonText} onGrowth={openPopulationGrowth} />
            <PopulationSummary nation={nation} housingProvided={housingProvided} housingSufficient={housingSufficient} />
            {generalPoints && <dl className="general-points">
              <div><dt><ItemIcon item={generalPoints} /></dt><dd>{generalPoints.amount}</dd></div>
              <div className="resource-adjust"><button type="button" onClick={openSpend}>{t("Spend.button")}</button><input aria-label={`${t("Home.change")} ${resourceNames[generalPoints.code]}`} type="number" step="1" value={resourceAmounts[generalPoints.code] ?? ""} onChange={(event) => setResourceAmounts({ ...resourceAmounts, [generalPoints.code]: event.target.value })} /><button type="button" onClick={() => adjustResource(generalPoints.code)}>{t("Common.add")}</button></div>
            </dl>}
            <dl className="resources">
              <div className="resource-head"><dt>{t("Home.resources")} <span className={`storage-capacity tooltip ${storageSufficient ? "sufficient" : "insufficient"}`} data-tooltip={t("Home.storageHint")} tabIndex="0">({storageUsed} / {storageCapacity})</span></dt><span>{t("Home.stock")}</span><span>{t("Home.perDaySpending")}</span><span>{t("Home.perDayIncome")}</span></div>
              {regularResources.map((resource) => (
                <div className="resource-row" key={resource.code}>
                  <dt><ItemIcon item={resource} /></dt><dd className={resource.code === "food" && nation.consecutive_hunger_days ? "resource-alert" : ""}>{resource.amount}</dd><span className="spending">−{resource.spending}</span><span className="income">+{resource.income}</span>
                </div>
              ))}
            </dl>
            <button className="manual-adjustment-button" type="button" onClick={() => setManualAdjustmentOpen(true)}>Manual Adjustment</button>
          </section>

          <section className="card event-log overview-event-log">
              <div className="section-heading"><h2>{t("Home.eventHistory")}</h2><a className="page-link" href="/logs">{t("Nav.logHistory")}</a></div>
              {logs.length === 0 ? <p>{t("Home.noEvents")}</p> : <ul>
                {logs.slice(0, 5).map((log) => <li key={log.id}><span>{t("Logs.entry", {day: log.day, message: log.message})}</span><strong className={log.amount < 0 ? "log-negative" : "log-positive"}>{log.amount > 0 ? "+" : ""}{log.amount}</strong></li>)}
              </ul>}
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
          {manualAdjustmentOpen && <div className="modal-backdrop">
            <section className="modal manual-adjustment-modal" role="dialog" aria-modal="true" aria-label="Manual Adjustment">
              <h2>Manual Adjustment</h2>
              <div className="manual-adjustment-list">
                {regularResources.map((resource) => <div className="manual-adjustment-row" key={resource.code}>
                  <span><ItemIcon item={resource} />{resourceNames[resource.code]}</span><strong>{resource.amount}</strong><input aria-label={`${t("Home.change")} ${resourceNames[resource.code]}`} type="number" step="1" value={resourceAmounts[resource.code] ?? ""} onChange={(event) => setResourceAmounts({ ...resourceAmounts, [resource.code]: event.target.value })} /><button type="button" onClick={() => adjustResource(resource.code)}>{t("Common.add")}</button>
                </div>)}
              </div>
              <div><button type="button" onClick={() => setManualAdjustmentOpen(false)}>{t("Common.close")}</button></div>
            </section>
          </div>}
        </>
      )}
    </main>
  );
}
