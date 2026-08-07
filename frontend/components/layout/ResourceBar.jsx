"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import GameIconFrame from "../game-art/GameIconFrame";
import ResourceAdjustmentModal from "../nation/ResourceAdjustmentModal";
import Toast from "../Toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function ResourceBar({ actions }) {
  const t = useTranslations("Data");
  const homeT = useTranslations("Home");
  const [resources, setResources] = useState([]);
  const [selectedResource, setSelectedResource] = useState(null);
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");

  async function loadResources() {
    const nationId = window.localStorage.getItem("nationId");
    if (!nationId) return;
    const response = await fetch(`${API_URL}/nations/${nationId}`);
    if (response.ok) setResources((await response.json()).resources || []);
  }

  useEffect(() => {
    loadResources().catch(() => {});
    const refreshResources = () => loadResources().catch(() => {});
    window.addEventListener("nation-resources-updated", refreshResources);
    return () => window.removeEventListener("nation-resources-updated", refreshResources);
  }, []);

  async function adjustResource() {
    const parsedAmount = Number(amount);
    if (!Number.isInteger(parsedAmount)) return setMessage(homeT("integerRequired"));
    try {
      const nationId = window.localStorage.getItem("nationId");
      const response = await fetch(`${API_URL}/nations/${nationId}/resources/${selectedResource.code}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ amount: parsedAmount }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");
      setSelectedResource(null);
      setAmount("");
      await loadResources();
      window.dispatchEvent(new Event("nation-resources-updated"));
    } catch (error) {
      setMessage(error.message);
    }
  }

  return <><Toast message={message} setMessage={setMessage} /><header className="resource-bar"><div className="resource-list">{resources.map((resource) => {
    const dailyBalance = resource.income - resource.spending;
    const label = t.has(`resources.${resource.code}`) ? t(`resources.${resource.code}`) : resource.name;
    const content = <><GameIconFrame src={resource.image_path} alt="" code={resource.code} size={38} variant="bare" /><div><strong>{resource.amount}</strong>{resource.code !== "general_points" && <small className={dailyBalance > 0 ? "positive" : dailyBalance < 0 ? "negative" : "neutral"}>{dailyBalance > 0 ? "+" : ""}{dailyBalance}/day</small>}</div><span className="sr-only">{label}</span></>;
    return resource.code !== "general_points" ? <button className="resource-bar-item resource-bar-button" type="button" key={resource.code} onClick={() => { setSelectedResource(resource); setAmount(""); }} aria-label={homeT("adjustResource", { resource: label })}>{content}</button> : <div className="resource-bar-item" key={resource.code}>{content}</div>;
  })}</div>{actions && <div className="resource-actions">{actions}</div>}</header>{selectedResource && <ResourceAdjustmentModal resource={{ ...selectedResource, name: t.has(`resources.${selectedResource.code}`) ? t(`resources.${selectedResource.code}`) : selectedResource.name }} value={amount} onChange={setAmount} onClose={() => setSelectedResource(null)} onApply={adjustResource} />}</>;
}
