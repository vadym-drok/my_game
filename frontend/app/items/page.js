"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import ItemIcon from "../../components/nation/ItemIcon";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function ItemList({ items, empty, t }) {
  return items.length === 0 ? <p>{empty}</p> : <ul className="items">{items.map((item) => <li key={item.id || item.code}><ItemIcon item={item} type="item" /><div><strong>{item.name}</strong><p>{item.description}</p><span>{t("workerDays", { amount: item.worker_days })} · {t("maxWorkers", { amount: item.max_workers })}</span></div></li>)}</ul>;
}

export default function ItemsPage() {
  const t = useTranslations("Items"); const router = useRouter(); const [items, setItems] = useState([]); const [owned, setOwned] = useState([]);
  useEffect(() => { const nationId = window.localStorage.getItem("nationId"); if (!nationId) return router.replace("/nations"); Promise.all([fetch(`${API_URL}/items`).then((response) => response.json()), fetch(`${API_URL}/nations/${nationId}/items`).then((response) => response.json())]).then(([available, existing]) => { setItems(available); setOwned(existing); }); }, []);
  return <main><header className="page-header"><div><p className="eyebrow">{t("eyebrow")}</p><h1>{t("title")}</h1></div></header><section className="grid"><section className="card"><h2>{t("available")}</h2><ItemList items={items} empty={t("empty")} t={t} /></section><section className="card"><h2>{t("owned")}</h2><ItemList items={owned} empty={t("noOwned")} t={t} /></section></section></main>;
}
