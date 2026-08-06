"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { Archive, Check, Plus, X } from "lucide-react";
import Toast from "../../components/Toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";
const taskTypes = ["one_time", "periodic", "infinite"];

export default function PersonalTasksPage() {
  const t = useTranslations(); const router = useRouter();
  const [nation, setNation] = useState(null); const [nationId, setNationId] = useState(""); const [tasks, setTasks] = useState([]); const [message, setMessage] = useState("");
  const activeTasks = tasks.filter((task) => task.status === "active");
  async function load(id) { try { const [nationData, taskData] = await Promise.all([fetch(`${API_URL}/nations/${id}`).then((response) => response.json()), fetch(`${API_URL}/nations/${id}/personal-tasks`).then((response) => response.json())]); setNation(nationData); setTasks(taskData); } catch { setMessage(t("PersonalTasks.createFailed")); } }
  useEffect(() => { const id = window.localStorage.getItem("nationId"); if (id) { setNationId(id); load(id); } else router.replace("/nations"); }, []);
  async function create(event) { event.preventDefault(); const form = event.currentTarget; const response = await fetch(`${API_URL}/nations/${nationId}/personal-tasks`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.fromEntries(new FormData(form))) }); if (!response.ok) return setMessage(t("PersonalTasks.createFailed")); form.reset(); setMessage(t("PersonalTasks.created")); await load(nationId); }
  async function update(task, action) { const response = await fetch(`${API_URL}/personal-tasks/${task.id}?action=${action}`, { method: "PATCH" }); if (!response.ok) return setMessage(t("PersonalTasks.updateFailed")); setMessage(action === "done" ? t("PersonalTasks.rewardAdded", { amount: task.reward }) : t("PersonalTasks.cancelled")); await load(nationId); }
  return <main><Toast message={message} setMessage={setMessage} /><header className="page-header"><div><p className="eyebrow">{t("Common.nationSimulator")}</p><h1>{t("PersonalTasks.title")}</h1></div><div className="page-header-actions"><Link className="button-secondary" href="/personal-tasks/archive"><Archive aria-hidden="true" />{t("PersonalTasks.archive")}</Link>{nation && <p className="page-day">{t("Common.day", { day: nation.current_day })}</p>}</div></header><section className="grid"><section className="card"><h2>{t("PersonalTasks.create")}</h2><form onSubmit={create}><label>{t("PersonalTasks.name")}<input name="name" maxLength="120" required placeholder={t("PersonalTasks.nameHint")} /></label><label>{t("PersonalTasks.description")}<textarea name="description" required placeholder={t("PersonalTasks.descriptionHint")} /></label><label>{t("PersonalTasks.reward")}<input name="reward" type="number" min="0" required /></label><label>{t("PersonalTasks.type")}<select name="task_type">{taskTypes.map((type) => <option key={type} value={type}>{t(`PersonalTaskTypes.${type}`)}</option>)}</select></label><button className="button-primary"><Plus aria-hidden="true" />{t("PersonalTasks.submit")}</button></form></section><section className="card"><h2>{t("PersonalTasks.active")}</h2>{activeTasks.length === 0 ? <p>{t("PersonalTasks.empty")}</p> : <ul className="personal-tasks">{activeTasks.map((task) => <li key={task.id}><div className="task-info"><strong>{task.name}</strong><span>{t(`PersonalTaskTypes.${task.task_type}`)} · {t("PersonalTasks.reward")}: {task.reward} ({t("PersonalTasks.completedCount", { count: task.counter })})</span><p>{task.description}</p></div><div className="task-actions"><button className="button-primary" type="button" onClick={() => update(task, "done")}><Check aria-hidden="true" />{t("PersonalTasks.done")}</button><button className="button-danger" type="button" onClick={() => update(task, "cancel")}><X aria-hidden="true" />{t("PersonalTasks.cancel")}</button></div></li>)}</ul>}</section></section></main>;
}
