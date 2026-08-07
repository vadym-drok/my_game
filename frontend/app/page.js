"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";
import { useRouter } from "next/navigation";
import { ArrowRightLeft, Coins, Hammer, History, Plus, Users, Warehouse, X } from "lucide-react";
import ItemIcon from "../components/nation/ItemIcon";
import PopulationSummary from "../components/nation/PopulationSummary";
import ResourceAdjustmentModal from "../components/nation/ResourceAdjustmentModal";
import Toast from "../components/Toast";
import GameIllustrationFrame from "../components/game-art/GameIllustrationFrame";
import PageHeader from "../components/layout/PageHeader";
import GameButton from "../components/ui/GameButton";
import GamePanel from "../components/ui/GamePanel";
import GameProgressBar from "../components/ui/GameProgressBar";
import SectionHeader from "../components/ui/SectionHeader";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
export default function Home() {
  const t = useTranslations();
  const dataT = useTranslations("Data");
  const overviewT = useTranslations("Overview");
  const router = useRouter();
  const [nationId, setNationId] = useState("");
  const [nation, setNation] = useState(null);
  const [logs, setLogs] = useState([]);
  const [processes, setProcesses] = useState([]);
  const [workTypes, setWorkTypes] = useState([]);
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
  const activeProcesses = processes.filter((process) => process.status === "active");
  const workTypesByCode = Object.fromEntries(workTypes.map((workType) => [workType.code, workType]));
  const housingProvided = nation?.housing_capacity ?? 0;
  const housingSufficient = housingProvided >= (nation?.population ?? 0);
  const populationGrowthLimit = Math.min(nation?.population_growth.max_increase ?? 0, Math.max(0, housingProvided - (nation?.population ?? 0)));
  const storageUsed = nation?.storage?.used ?? 0;
  const storageCapacity = nation?.storage?.capacity ?? 0;
  const storageSufficient = storageCapacity >= storageUsed;
  const availableWorkers = Math.max(0, (nation?.active_population ?? 0) - activeProcesses.reduce((total, process) => total + process.assigned_workers, 0));
  const food = regularResources.find((resource) => resource.code === "food");
  const foodReserveDays = food?.spending > 0 ? Math.floor(food.amount / food.spending) : null;
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

  useEffect(() => {
    const refreshStatus = () => {
      const savedId = window.localStorage.getItem("nationId");
      if (savedId) request(`/nations/${savedId}`).then(setNation).catch((error) => setMessage(error.message));
    };
    window.addEventListener("nation-resources-updated", refreshStatus);
    return () => window.removeEventListener("nation-resources-updated", refreshStatus);
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
      const [data, eventLogs, processData, workTypeData] = await Promise.all([
        request(`/nations/${id}`), request(`/nations/${id}/logs`), request(`/nations/${id}/processes`).catch(() => []), request("/work-rules").catch(() => []),
      ]);
      setNationId(String(id));
      window.localStorage.setItem("nationId", String(id));
      setNation(data);
      setLogs(eventLogs);
      setProcesses(processData);
      setWorkTypes(workTypeData);
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
    setGrowthAmount(populationGrowthLimit);
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
      window.dispatchEvent(new Event("nation-resources-updated"));
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
      window.dispatchEvent(new Event("nation-resources-updated"));
      setMessage(t("Spend.purchased", { amount, resource: resourceNames[resource.code] }));
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main>
      <Toast message={message} setMessage={setMessage} />
      {!nation ? <p>{t("Common.loading")}</p> : (
        <>
          <PageHeader eyebrow={t("Home.nationNumber", { id: nation.id })} title={nation.name} actions={<div className="overview-nation-actions"><p className="page-day">{t("Common.day", { day: nation.current_day })}</p><GameButton className={`growth-button ${nation.hunger.active ? "hunger" : ""}`} disabled={!nation.population_growth.available} onClick={openPopulationGrowth}>{growthButtonText}</GameButton></div>} />

          <section className="overview-status-grid">
            <GamePanel className="overview-population-panel">
              <SectionHeader icon={Users} title={t("Home.population")} />
              <PopulationSummary nation={nation} housingProvided={housingProvided} housingSufficient={housingSufficient} />
            </GamePanel>
            <GamePanel className="overview-settlement-panel">
              <SectionHeader icon={Warehouse} title={overviewT("settlementStatus")} />
              <div className="settlement-status-grid">
                <div className="settlement-status-column">
                  <div className="settlement-metric"><div><strong>{dataT("buildingTypes.housing")}</strong><span>{nation.population} / {housingProvided}</span></div><GameProgressBar value={Math.min(nation.population, housingProvided)} max={housingProvided || 1} className={!housingSufficient ? "is-overflow" : ""} /></div>
                  <div className="settlement-metric"><div><strong>{dataT("buildingTypes.warehouse")}</strong><span className={storageSufficient ? "storage-capacity sufficient" : "storage-capacity insufficient"}>{storageUsed} / {storageCapacity}</span></div><GameProgressBar value={Math.min(storageUsed, storageCapacity)} max={storageCapacity || 1} className={!storageSufficient ? "is-overflow" : ""} /></div>
                </div>
                <div className="settlement-status-column">
                  <div className="settlement-metric settlement-food-reserve"><strong>{overviewT("foodReserve")}</strong><span>{foodReserveDays === null ? "—" : overviewT("days", { days: foodReserveDays })}</span></div>
                  <div className="settlement-metric"><div><strong>{overviewT("workersAvailable")}</strong><span>{availableWorkers} / {nation.active_population}</span></div><GameProgressBar value={availableWorkers} max={nation.active_population || 1} /></div>
                </div>
              </div>
            </GamePanel>
          </section>

          {generalPoints && <GamePanel className="overview-general-points general-points">
              <SectionHeader icon={Coins} title={t("Home.generalPoints")} />
              <div className="general-points-content"><div className="general-points-value"><ItemIcon item={generalPoints} /><strong>{generalPoints.amount}</strong></div><div className="resource-adjust"><input aria-label={`${t("Home.change")} ${resourceNames[generalPoints.code]}`} type="number" step="1" value={resourceAmounts[generalPoints.code] ?? ""} onChange={(event) => setResourceAmounts({ ...resourceAmounts, [generalPoints.code]: event.target.value })} /><GameButton type="button" onClick={() => adjustResource(generalPoints.code)}><Plus aria-hidden="true" />{t("Home.addPoints")}</GameButton><GameButton type="button" onClick={openSpend}><ArrowRightLeft aria-hidden="true" />{t("Spend.button")}</GameButton></div></div>
          </GamePanel>}

          {activeProcesses.length > 0 && <GamePanel className="overview-processes">
            <SectionHeader icon={Hammer} title={t("Home.currentProcesses")}><a className="button-secondary" href="/processes">{t("Nav.processes")}</a></SectionHeader>
            <div className="process-preview-list">{activeProcesses.slice(0, 3).map((process) => {
              const workType = workTypesByCode[process.work_type];
              return <article className="process-preview" key={process.id}><GameIllustrationFrame src={workType?.image_path} alt={workType?.name || process.work_type} code={process.work_type} ratio="4 / 3" className="process-preview-artwork" /><div><strong>{process.name}</strong><span>{t("History.workers", { amount: process.assigned_workers })}</span>{process.mode === "finite" && <span>{process.completed_worker_days} / {process.required_worker_days} {t("Home.workerDays")}</span>}</div></article>;
            })}</div>
          </GamePanel>}

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
          {selectedResource && <ResourceAdjustmentModal resource={{ ...selectedResource, name: resourceNames[selectedResource.code] }} value={resourceAmounts[selectedResource.code] ?? ""} onChange={(amount) => setResourceAmounts({ ...resourceAmounts, [selectedResource.code]: amount })} onClose={() => setSelectedResource(null)} onApply={() => adjustResource(selectedResource.code)} />}
        </>
      )}
    </main>
  );
}
