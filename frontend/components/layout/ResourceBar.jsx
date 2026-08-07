"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import GameIconFrame from "../game-art/GameIconFrame";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function ResourceBar({ actions }) {
  const t = useTranslations("Data");
  const [resources, setResources] = useState([]);

  useEffect(() => {
    const nationId = window.localStorage.getItem("nationId");
    if (!nationId) return;
    fetch(`${API_URL}/nations/${nationId}`).then((response) => response.ok ? response.json() : null).then((nation) => setResources(nation?.resources || [])).catch(() => {});
  }, []);

  return <header className="resource-bar">
    <div className="resource-list">
      {resources.map((resource) => {
        const dailyBalance = resource.income - resource.spending;
        return <div className="resource-bar-item" key={resource.code}>
          <GameIconFrame src={resource.image_path} alt="" code={resource.code} size={38} variant="bare" />
          <div><strong>{resource.amount}</strong>{resource.code !== "general_points" && <small className={dailyBalance > 0 ? "positive" : dailyBalance < 0 ? "negative" : "neutral"}>{dailyBalance > 0 ? "+" : ""}{dailyBalance}/day</small>}</div>
          <span className="sr-only">{t.has(`resources.${resource.code}`) ? t(`resources.${resource.code}`) : resource.name}</span>
        </div>;
      })}
    </div>
    {actions && <div className="resource-actions">{actions}</div>}
  </header>;
}
