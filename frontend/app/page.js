"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";
import { useRouter } from "next/navigation";
import { ArrowRightLeft, Coins, History, Plus, Users, Warehouse, X } from "lucide-react";
import ItemIcon from "../components/nation/ItemIcon";
import NationHeader from "../components/nation/NationHeader";
import PopulationSummary from "../components/nation/PopulationSummary";
import Toast from "../components/Toast";
import GameButton from "../components/ui/GameButton";
import GamePanel from "../components/ui/GamePanel";
import SectionHeader from "../components/ui/SectionHeader";

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
  const [selectedResource, setSelectedResource] = useState(null);
  const [purchaseAmounts, setPurchaseAmounts] = useState({});
  const [resourceAmounts, setResourceAmounts] = useState({});
  const resourceNames = Object.fromEntries((nation?.resources || []).map((resource) => [resource.code, dataT(`resources.${resource.code}`, {default: resource.name})]));
  const generalPoints = nation?.resources?.find((resource) => resource.code === "general_points");
  const regularResources = (nation?.resources || []).filter((resource) => resource.code !== "general_points");
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
      setSelectedResource(null);
    } catch (error) {
      setMessage(error.message);
    }
  }

  function openSpend() {
    setPurchaseAmounts({});
    setSpendModalOpen(true);
  }

  function openResourceAdjustment(resource) {
    setResourceAmounts({ ...resourceAmounts, [resource.code]: "" });
    setSelectedResource(resource);
  }

  async function purchaseResource(resource) {
    const amount = Number(purchaseAmounts[resource.code]);
    if (!Number.isInteger(amount) || amount < 1) return setMessage(t("Spend.nothing"));
    try {
      await request(`/nations/${nationId}/resource-purchases`, {
        method: "POST",
        body: JSON.stringify({ resources: { [resource.code]: amount } }),
      });
      setSpendModalOpen(false);
      setPurchaseAmounts({ ...purchaseAmounts, [resource.code]: "" });
      await loadNation();
      setMessage(t("Spend.purchased", { amount, resource: resourceNames[resource.code] }));
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main>
      <Toast message={message} setMessage={setMessage} />
      <header>
        <p className="eyebrow">{t("Common.nationSimulator")}</p>
        <div className="app-title"><h1>{t("Home.title")}</h1></div>
      </header>

      {!nation ? <p>{t("Common.loading")}</p> : (
        <>
          <GamePanel className="nation">
            <NationHeader nation={nation} growthButtonText={growthButtonText} onGrowth={openPopulationGrowth} />
            <section className="overview-section population-section">
              <SectionHeader icon={Users} title={t("Home.population")} />
              <PopulationSummary nation={nation} housingProvided={housingProvided} housingSufficient={housingSufficient} />
            </section>
            {generalPoints && <section className="overview-section general-points">
              <SectionHeader icon={Coins} title={t("Home.generalPoints")} />
              <div className="general-points-content"><div className="general-points-value"><ItemIcon item={generalPoints} /><strong>{generalPoints.amount}</strong></div><div className="resource-adjust"><input aria-label={`${t("Home.change")} ${resourceNames[generalPoints.code]}`} type="number" step="1" value={resourceAmounts[generalPoints.code] ?? ""} onChange={(event) => setResourceAmounts({ ...resourceAmounts, [generalPoints.code]: event.target.value })} /><GameButton type="button" onClick={() => adjustResource(generalPoints.code)}><Plus aria-hidden="true" />{t("Home.addPoints")}</GameButton><GameButton type="button" onClick={openSpend}><ArrowRightLeft aria-hidden="true" />{t("Spend.button")}</GameButton></div></div>
            </section>}
            <section className="overview-section resources-section">
              <SectionHeader icon={Warehouse} title={t("Home.resources")}><span className={`storage-capacity tooltip ${storageSufficient ? "sufficient" : "insufficient"}`} data-tooltip={t("Home.storageHint")} tabIndex="0">({storageUsed} / {storageCapacity})</span></SectionHeader>
              <div className="resources-grid">
                {regularResources.map((resource) => {
                  const dailyBalance = resource.income - resource.spending;
                  return <button className="button-secondary resource-card" type="button" key={resource.code} onClick={() => openResourceAdjustment(resource)} aria-label={t("Home.adjustResource", { resource: resourceNames[resource.code] })}>
                    <span className="resource-card-name"><ItemIcon item={resource} />{resourceNames[resource.code]}</span>
                    <span className="resource-card-stats"><strong className={resource.code === "food" && resource.amount === 0 ? "resource-danger" : ""}>{resource.amount}</strong><span className={dailyBalance < 0 ? "resource-warning" : dailyBalance > 0 ? "resource-success" : "resource-secondary"}>{t("Home.dailyChange", { amount: dailyBalance > 0 ? `+${dailyBalance}` : dailyBalance })}</span></span>
                  </button>;
                })}
              </div>
            </section>
          </GamePanel>

          <GamePanel className="event-log overview-event-log">
              <SectionHeader icon={History} title={t("Home.eventHistory")}><a className="button-secondary" href="/logs">{t("Nav.logHistory")}</a></SectionHeader>
              {logs.length === 0 ? <p>{t("Home.noEvents")}</p> : <ul>
                {logs.slice(0, 5).map((log) => <li key={log.id}><span>{t("Logs.entry", {day: log.day, message: log.message})}</span><strong className={log.amount < 0 ? "log-negative" : "log-positive"}>{log.amount > 0 ? "+" : ""}{log.amount}</strong></li>)}
              </ul>}
          </GamePanel>

          {growthModalOpen && <div className="modal-backdrop">
            <form className="modal" onSubmit={applyPopulationGrowth}>
              <button className="button-secondary button-icon modal-close" type="button" aria-label={t("Common.close")} onClick={() => setGrowthModalOpen(false)}><X aria-hidden="true" /></button>
              <h2>{t("Home.growthTitle")}</h2>
              <p>{t("Home.availableUpTo", {amount: populationGrowthLimit})}</p>
              <label>{t("Home.addPopulation")}<span className="adjustment-controls"><input type="number" min="0" max={populationGrowthLimit} value={growthAmount} onChange={(event) => setGrowthAmount(event.target.value)} /><button className="button-primary">{t("Common.apply")}</button></span></label>
            </form>
          </div>}
          {spendModalOpen && <div className="modal-backdrop">
            <section className="modal spend-modal" role="dialog" aria-modal="true" aria-label={t("Spend.title")}>
              <button className="button-secondary button-icon modal-close" type="button" aria-label={t("Common.close")} onClick={() => setSpendModalOpen(false)}><X aria-hidden="true" /></button>
              <h2>{t("Spend.title")}</h2>
              <p>{t("Spend.available", {amount: generalPoints.amount})}</p>
              <div className="purchase-list">{regularResources.map((resource) => <div className="purchase-row" key={resource.code}><span className="purchase-resource"><ItemIcon item={resource} /><strong>{resource.amount}</strong></span><input aria-label={`${t("Spend.confirm")} ${resourceNames[resource.code]}`} type="number" min="0" step="1" value={purchaseAmounts[resource.code] ?? ""} onChange={(event) => setPurchaseAmounts({...purchaseAmounts, [resource.code]: event.target.value})} /><button className="button-primary" type="button" onClick={() => purchaseResource(resource)}>{t("Spend.confirm")}</button></div>)}</div>
            </section>
          </div>}
          {selectedResource && <div className="modal-backdrop">
            <section className="modal manual-adjustment-modal" role="dialog" aria-modal="true" aria-label={t("Home.manualAdjustment")}>
              <button className="button-secondary button-icon modal-close" type="button" aria-label={t("Common.close")} onClick={() => setSelectedResource(null)}><X aria-hidden="true" /></button>
              <h2>{t("Home.manualAdjustment")}</h2>
              <p className="adjustment-resource"><ItemIcon item={selectedResource} />{resourceNames[selectedResource.code]}</p>
              <p>{t("Home.currentAmount", { amount: selectedResource.amount })}</p>
              <label>{t("Home.change")}<span className="adjustment-controls"><input aria-label={`${t("Home.change")} ${resourceNames[selectedResource.code]}`} type="number" step="1" value={resourceAmounts[selectedResource.code] ?? ""} onChange={(event) => setResourceAmounts({ ...resourceAmounts, [selectedResource.code]: event.target.value })} /><button className="button-primary" type="button" onClick={() => adjustResource(selectedResource.code)}>{t("Home.applyAdjustment")}</button></span></label>
            </section>
          </div>}
        </>
      )}
    </main>
  );
}
