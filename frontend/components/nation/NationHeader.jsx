import { useTranslations } from "next-intl";

export default function NationHeader({ nation, growthButtonText, onGrowth }) {
  const t = useTranslations();
  return <><div><p className="eyebrow">{t("Home.nationNumber", { id: nation.id })}</p><h2>{nation.name}</h2><button className={`growth-button ${nation.hunger.active ? "hunger" : ""}`} disabled={!nation.population_growth.available} onClick={onGrowth}>{growthButtonText}</button></div><p className="start-date"><span>{t("Common.day", { day: nation.current_day })}</span></p></>;
}
