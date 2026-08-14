"use client";

import { useEffect, useState } from "react";
import {useTranslations} from "next-intl";
import { useRouter } from "next/navigation";
import { Hammer, History, Warehouse, X } from "lucide-react";
import PopulationSummary from "../components/nation/PopulationSummary";
import Toast from "../components/Toast";
import GameIconFrame from "../components/game-art/GameIconFrame";
import GameIllustrationFrame from "../components/game-art/GameIllustrationFrame";
import GamePanel from "../components/ui/GamePanel";
import GameProgressBar from "../components/ui/GameProgressBar";
import SectionHeader from "../components/ui/SectionHeader";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
function PopulationArtworkIcon() {
  return <GameIconFrame src="/images/general/population.png" alt="" code="population" size={24} />;
}

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
  const regularResources = (nation?.resources || []).filter((resource) => resource.code !== "general_points");
  const activeProcesses = processes.filter((process) => process.status === "active");
  const workTypesByCode = Object.fromEntries(workTypes.map((workType) => [workType.code, workType]));
  const housingProvided = nation?.housing_capacity ?? 0;
  const housingSufficient = housingProvided >= (nation?.population ?? 0);
  const populationGrowthLimit = Math.min(nation?.population_growth.max_increase ?? 0, Math.max(0, housingProvided - (nation?.population ?? 0)));
  const storageUsed = nation?.storage?.used ?? 0;
  const storageCapacity = nation?.storage?.capacity ?? 0;
  const storageSufficient = storageCapacity >= storageUsed;
  const workingWorkers = activeProcesses.reduce((total, process) => total + process.assigned_workers, 0);
  const availableWorkers = Math.max(0, (nation?.active_population ?? 0) - workingWorkers);
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

  return (
    <main>
      <Toast message={message} setMessage={setMessage} />
      {!nation ? <p>{t("Common.loading")}</p> : (
        <>
          <section className="overview-status-grid">
            <GamePanel className="overview-population-panel">
              <SectionHeader icon={PopulationArtworkIcon} title={t("Home.population")} />
              <PopulationSummary nation={nation} housingProvided={housingProvided} housingSufficient={housingSufficient} growthButtonText={growthButtonText} onGrowth={openPopulationGrowth} />
            </GamePanel>
            <GamePanel className="overview-settlement-panel">
              <SectionHeader icon={Warehouse} title={overviewT("settlementStatus")} />
              <div className="settlement-status-grid">
                <div className="settlement-status-column">
                  <div className="settlement-metric"><div><strong>{dataT("buildingTypes.housing")}</strong><span>{nation.population} / {housingProvided}</span></div><GameProgressBar value={Math.min(nation.population, housingProvided)} max={housingProvided || 1} className={!housingSufficient ? "is-overflow" : ""} /></div>
                  <div className="settlement-metric"><div><strong>{overviewT("storage")}</strong><span className={storageSufficient ? "storage-capacity sufficient" : "storage-capacity insufficient"}>{storageUsed} / {storageCapacity}</span></div><GameProgressBar value={Math.min(storageUsed, storageCapacity)} max={storageCapacity || 1} className={!storageSufficient ? "is-overflow" : ""} /></div>
                </div>
                <div className="settlement-status-column">
                  <div className="settlement-metric settlement-food-reserve"><strong>{overviewT("foodReserve")}</strong><span>{foodReserveDays === null ? "—" : overviewT("days", { days: foodReserveDays })}</span></div>
                  <div className="settlement-metric settlement-workforce"><div><strong>{overviewT("workforce")}</strong><span>{overviewT("workforceSummary", { working: workingWorkers, available: availableWorkers })}</span></div><GameProgressBar value={workingWorkers} max={nation.active_population || 1} /></div>
                </div>
              </div>
            </GamePanel>
          </section>

          {activeProcesses.length > 0 && <GamePanel className="overview-processes">
            <SectionHeader icon={Hammer} title={t("Home.currentProcesses")}><a className="button-secondary" href="/processes">{t("Nav.processes")}</a></SectionHeader>
            <div className="process-preview-list">{activeProcesses.slice(0, 3).map((process) => {
              const workType = workTypesByCode[process.work_type];
              const remainingWorkerDays = Math.max(0, (process.required_worker_days || 0) - process.completed_worker_days);
              const remainingDays = process.assigned_workers > 0 ? Math.ceil(remainingWorkerDays / process.assigned_workers) : null;
              const title = dataT(`workTypes.${process.work_type}`, { default: workType?.name || process.work_type });
              const outputName = process.outputs?.building?.name || process.outputs?.item?.name;
              return <article className="process-preview" key={process.id}><GameIllustrationFrame src={workType?.image_path} alt={title} code={process.work_type} ratio="4 / 3" className="process-preview-artwork" /><div><strong>{title}{outputName && `: ${outputName}`}</strong>{process.description && <span>{process.description}</span>}<span>{t("History.workers", { amount: process.assigned_workers })}</span>{process.mode === "finite" && <><span className="tooltip process-progress-tooltip" data-tooltip={overviewT("completedWorkerDays", { completed: process.completed_worker_days, required: process.required_worker_days })} tabIndex="0"><GameProgressBar value={process.completed_worker_days} max={process.required_worker_days || 1} /></span><div className="process-preview-remaining">{remainingDays !== null && <span>{overviewT("remainingDays", { days: remainingDays })}</span>}</div></>}</div></article>;
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
        </>
      )}
    </main>
  );
}
