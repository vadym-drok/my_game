"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
const taskTypes = ["one_time", "periodic", "infinite"];

export default function PersonalTasksPage() {
  const t = useTranslations(); const router = useRouter();
  const [nation, setNation] = useState(null); const [nationId, setNationId] = useState(""); const [tasks, setTasks] = useState([]); const [message, setMessage] = useState("");
  const activeTasks = tasks.filter((task) => task.status === "active");
  async function load(id) { try { const [nationData, taskData] = await Promise.all([fetch(`${API_URL}/nations/${id}`).then((response) => response.json()), fetch(`${API_URL}/nations/${id}/personal-tasks`).then((response) => response.json())]); setNation(nationData); setTasks(taskData); } catch { setMessage(t("PersonalTasks.createFailed")); } }
  useEffect(() => { const id = window.localStorage.getItem("nationId"); if (id) { setNationId(id); load(id); } else router.replace("/nations"); }, []);
  async function create(event) { event.preventDefault(); const form = event.currentTarget; const response = await fetch(`${API_URL}/nations/${nationId}/personal-tasks`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.fromEntries(new FormData(form))) }); if (!response.ok) return setMessage(t("PersonalTasks.createFailed")); form.reset(); setMessage(t("PersonalTasks.created")); await load(nationId); }
  return <main><header className="page-header"><div><p className="eyebrow">{t("Common.nationSimulator")}</p><h1>{t("PersonalTasks.title")}</h1></div>{nation && <p className="page-day">{t("Common.day", { day: nation.current_day })}</p>}</header>{message && <p className="message">{message}</p>}<section className="grid"><section className="card"><h2>{t("PersonalTasks.create")}</h2><form onSubmit={create}><label>{t("PersonalTasks.name")}<input name="name" maxLength="120" required placeholder={t("PersonalTasks.nameHint")} /></label><label>{t("PersonalTasks.description")}<textarea name="description" required placeholder={t("PersonalTasks.descriptionHint")} /></label><label>{t("PersonalTasks.reward")}<input name="reward" type="number" min="0" required /></label><label>{t("PersonalTasks.type")}<select name="task_type">{taskTypes.map((type) => <option key={type} value={type}>{t(`PersonalTaskTypes.${type}`)}</option>)}</select></label><button>{t("PersonalTasks.submit")}</button></form></section><section className="card"><h2>{t("PersonalTasks.active")}</h2>{activeTasks.length === 0 ? <p>{t("PersonalTasks.empty")}</p> : <ul className="personal-tasks">{activeTasks.map((task) => <li key={task.id}><strong>{task.name}</strong><span>{t(`PersonalTaskTypes.${task.task_type}`)} · {t("PersonalTasks.reward")}: {task.reward}</span><p>{task.description}</p></li>)}</ul>}</section></section></main>;
}
