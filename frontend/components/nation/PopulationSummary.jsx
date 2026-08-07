import { useTranslations } from "next-intl";
import GameButton from "../ui/GameButton";

export default function PopulationSummary({ nation, housingProvided, housingSufficient, growthButtonText, onGrowth }) {
  const t = useTranslations();
  const progress = housingProvided > 0 ? Math.min(100, nation.population / housingProvided * 100) : 0;
  return <div className="population-summary"><div className={`population-ring ${housingSufficient ? "sufficient" : "insufficient"}`} role="img" aria-label={`${nation.population} / ${housingProvided}`}><svg viewBox="0 0 42 42" aria-hidden="true"><circle className="population-ring-track" cx="21" cy="21" r="16" pathLength="100" /><circle className="population-ring-value" cx="21" cy="21" r="16" pathLength="100" strokeDasharray={`${progress} 100`} /></svg><span><strong>{nation.population}</strong><small> / {housingProvided}</small></span></div><div className="population-details"><dl className="population"><div><dt>{t("Home.activePopulation")}</dt><dd>{nation.active_population}</dd></div><div><dt>{t("Home.passivePopulation")}</dt><dd>{nation.passive_population}</dd></div></dl><GameButton className={`growth-button ${nation.hunger.active ? "hunger" : ""}`} disabled={!nation.population_growth.available} onClick={onGrowth}>{growthButtonText}</GameButton></div></div>;
}
