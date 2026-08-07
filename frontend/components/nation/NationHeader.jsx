"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import PageHeader from "../layout/PageHeader";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function NationHeader() {
  const t = useTranslations(); const [nation, setNation] = useState(null);
  useEffect(() => { const load = () => { const id = window.localStorage.getItem("nationId"); if (!id) return setNation(null); fetch(`${API_URL}/nations/${id}`).then((response) => response.ok ? response.json() : null).then(setNation).catch(() => setNation(null)); }; load(); window.addEventListener("nation-resources-updated", load); return () => window.removeEventListener("nation-resources-updated", load); }, []);
  return nation && <PageHeader className="nation-page-header" title={nation.name} artwork="/images/general/nation_overview_header.webp" artworkAlt="" artworkPosition="52% 100%" actions={<p className="page-day">{t("Common.day", { day: nation.current_day })}</p>} />;
}
