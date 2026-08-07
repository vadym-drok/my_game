"use client";

import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import GameIconFrame from "../game-art/GameIconFrame";
import ResourceAdjustmentModal from "../nation/ResourceAdjustmentModal";
import ItemIcon from "../nation/ItemIcon";
import Toast from "../Toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function ResourceBar({ actions }) {
  const t = useTranslations("Data");
  const homeT = useTranslations("Home");
  const spendT = useTranslations("Spend");
  const commonT = useTranslations("Common");
  const [resources, setResources] = useState([]);
  const [selectedResource, setSelectedResource] = useState(null);
  const [amount, setAmount] = useState("");
  const [spendModalOpen, setSpendModalOpen] = useState(false);
  const [purchaseAmounts, setPurchaseAmounts] = useState({});
  const [message, setMessage] = useState("");
  const generalPoints = resources.find((resource) => resource.code === "general_points");
  const regularResources = resources.filter((resource) => resource.code !== "general_points");

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

  async function purchaseResource(resource) {
    const purchaseAmount = Number(purchaseAmounts[resource.code]);
    if (!Number.isInteger(purchaseAmount) || purchaseAmount < 1) return setMessage(spendT("nothing"));
    try {
      const nationId = window.localStorage.getItem("nationId");
      const response = await fetch(`${API_URL}/nations/${nationId}/resource-purchases`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resources: { [resource.code]: purchaseAmount } }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");
      setSpendModalOpen(false);
      setPurchaseAmounts({ ...purchaseAmounts, [resource.code]: "" });
      await loadResources();
      window.dispatchEvent(new Event("nation-resources-updated"));
      setMessage(spendT("purchased", { amount: purchaseAmount, resource: t.has(`resources.${resource.code}`) ? t(`resources.${resource.code}`) : resource.name }));
    } catch (error) {
      setMessage(error.message);
    }
  }

  return <><Toast message={message} setMessage={setMessage} /><header className="resource-bar"><div className="resource-list">{resources.map((resource) => {
    const dailyBalance = resource.income - resource.spending;
    const label = t.has(`resources.${resource.code}`) ? t(`resources.${resource.code}`) : resource.name;
    const content = <><GameIconFrame src={resource.image_path} alt="" code={resource.code} size={38} variant="bare" /><div><strong>{resource.amount}</strong>{resource.code !== "general_points" && <small className={dailyBalance > 0 ? "positive" : dailyBalance < 0 ? "negative" : "neutral"}>{dailyBalance > 0 ? "+" : ""}{dailyBalance}/day</small>}</div><span className="sr-only">{label}</span></>;
    if (resource.code === "general_points") return <div className="resource-bar-item resource-system-item" key={resource.code}><button className="resource-bar-button" type="button" onClick={() => { setSelectedResource(resource); setAmount(""); }} aria-label={homeT("adjustResource", { resource: label })}>{content}</button><button className="resource-convert-button" type="button" onClick={() => { setPurchaseAmounts({}); setSpendModalOpen(true); }}>{spendT("button")}</button></div>;
    return <button className="resource-bar-item resource-bar-button" type="button" key={resource.code} onClick={() => { setSelectedResource(resource); setAmount(""); }} aria-label={homeT("adjustResource", { resource: label })}>{content}</button>;
  })}</div>{actions && <div className="resource-actions">{actions}</div>}</header>{selectedResource && <ResourceAdjustmentModal resource={{ ...selectedResource, name: t.has(`resources.${selectedResource.code}`) ? t(`resources.${selectedResource.code}`) : selectedResource.name }} value={amount} onChange={setAmount} onClose={() => setSelectedResource(null)} onApply={adjustResource} />}{spendModalOpen && generalPoints && <div className="modal-backdrop"><section className="modal spend-modal" role="dialog" aria-modal="true" aria-label={spendT("title")}><button className="button-secondary button-icon modal-close" type="button" aria-label={commonT("close")} onClick={() => setSpendModalOpen(false)}><X aria-hidden="true" /></button><h2>{spendT("title")}</h2><p>{spendT("available", { amount: generalPoints.amount })}</p><div className="purchase-list">{regularResources.map((resource) => <div className="purchase-row" key={resource.code}><span className="purchase-resource"><ItemIcon item={resource} /><strong>{resource.amount}</strong></span><input aria-label={`${spendT("confirm")} ${t.has(`resources.${resource.code}`) ? t(`resources.${resource.code}`) : resource.name}`} type="number" min="0" step="1" value={purchaseAmounts[resource.code] ?? ""} onChange={(event) => setPurchaseAmounts({ ...purchaseAmounts, [resource.code]: event.target.value })} /><button className="button-primary" type="button" onClick={() => purchaseResource(resource)}>{spendT("confirm")}</button></div>)}</div></section></div>}</>;
}
