import { useTranslations } from "next-intl";
import GameIconFrame from "../game-art/GameIconFrame";

export default function PopulationSummary({ nation, housingProvided, housingSufficient }) {
  const t = useTranslations();
  return <div className="population-summary"><GameIconFrame src="/images/general/population.png" alt="" code="population" size={48} /><dl className="population"><div><dt>{t("Home.population")}</dt><dd className="tooltip" data-tooltip={t("Home.populationHousingHint")} tabIndex="0">{nation.population} <span className={`housing-capacity ${housingSufficient ? "sufficient" : "insufficient"}`}>({housingProvided})</span></dd></div><div><dt>{t("Home.activePopulation")}</dt><dd>{nation.active_population}</dd></div><div><dt>{t("Home.passivePopulation")}</dt><dd>{nation.passive_population}</dd></div></dl></div>;
}
