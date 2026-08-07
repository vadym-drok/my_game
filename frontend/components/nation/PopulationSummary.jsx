import { useTranslations } from "next-intl";
import GameIconFrame from "../game-art/GameIconFrame";

export default function PopulationSummary({ nation, housingProvided, housingSufficient }) {
  const t = useTranslations();
  const progress = housingProvided > 0 ? Math.min(100, nation.population / housingProvided * 100) : 0;
  return <div className="population-summary"><div className={`population-ring ${housingSufficient ? "sufficient" : "insufficient"}`} role="img" aria-label={`${nation.population} / ${housingProvided}`}><svg viewBox="0 0 42 42" aria-hidden="true"><circle className="population-ring-track" cx="21" cy="21" r="16" pathLength="100" /><circle className="population-ring-value" cx="21" cy="21" r="16" pathLength="100" strokeDasharray={`${progress} 100`} /></svg><span><strong>{nation.population}</strong><small> / {housingProvided}</small></span></div><dl className="population"><div><dt><GameIconFrame src="/images/general/population.png" alt="" code="population" size={28} />{t("Home.activePopulation")}</dt><dd>{nation.active_population}</dd></div><div><dt>{t("Home.passivePopulation")}</dt><dd>{nation.passive_population}</dd></div></dl></div>;
}
