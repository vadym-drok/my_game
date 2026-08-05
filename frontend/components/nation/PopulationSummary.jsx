import { useTranslations } from "next-intl";

export default function PopulationSummary({ nation, housingProvided, housingSufficient }) {
  const t = useTranslations();
  return <dl className="population"><div><dt>{t("Home.population")}</dt><dd className="tooltip" data-tooltip={t("Home.populationHousingHint")} tabIndex="0">{nation.population} <span className={`housing-capacity ${housingSufficient ? "sufficient" : "insufficient"}`}>({housingProvided})</span></dd></div><div><dt>{t("Home.activePopulation")}</dt><dd>{nation.active_population}</dd></div><div><dt>{t("Home.passivePopulation")}</dt><dd>{nation.passive_population}</dd></div></dl>;
}
