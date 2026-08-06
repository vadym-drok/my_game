"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { ArrowLeft, Play, RotateCcw } from "lucide-react";
import Toast from "../../../components/Toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function TaskList({ tasks, empty, t, update }) {
  return tasks.length === 0 ? <p>{t(empty)}</p> : <ul className="personal-tasks">{tasks.map((task) => <li key={task.id} className={task.status === "cancelled" && task.counter > 0 ? "was-completed" : ""}><div className="task-info"><strong>{task.name}</strong><span>{t(`PersonalTaskTypes.${task.task_type}`)} · {t("PersonalTasks.reward")}: {task.reward}{task.status === "cancelled" && ` (${t("PersonalTasks.completedCount", { count: task.counter })})`}</span><p>{task.description}</p></div>{task.status === "cancelled" && task.task_type !== "one_time" && <div className="task-actions"><button className="button-warning" type="button" onClick={() => update(task.id, "restart")}><RotateCcw aria-hidden="true" />{t("PersonalTasks.restart")}</button><button className="button-primary" type="button" onClick={() => update(task.id, "continue")}><Play aria-hidden="true" />{t("PersonalTasks.continue")}</button></div>}</li>)}</ul>;
}

export default function PersonalTaskArchivePage() {
  const t = useTranslations(); const router = useRouter(); const [tasks, setTasks] = useState([]); const [message, setMessage] = useState("");
  async function load(nationId) { const response = await fetch(`${API_URL}/nations/${nationId}/personal-tasks`); setTasks(await response.json()); }
  useEffect(() => { const nationId = window.localStorage.getItem("nationId"); if (!nationId) return router.replace("/nations"); load(nationId); }, []);
  async function update(taskId, action) { const response = await fetch(`${API_URL}/personal-tasks/${taskId}?action=${action}`, { method: "PATCH" }); if (!response.ok) return setMessage(t("PersonalTasks.updateFailed")); await load(window.localStorage.getItem("nationId")); setMessage(t(action === "restart" ? "PersonalTasks.restartSuccess" : "PersonalTasks.continueSuccess")); }
  const finished = tasks.filter((task) => task.status === "done" && task.task_type === "one_time"); const archived = tasks.filter((task) => task.status === "cancelled");
  return <main><Toast message={message} setMessage={setMessage} /><header className="page-header"><div><p className="eyebrow">{t("Common.nationSimulator")}</p><h1>{t("PersonalTasks.archiveTitle")}</h1></div><Link className="button-secondary" href="/personal-tasks"><ArrowLeft aria-hidden="true" />{t("PersonalTasks.back")}</Link></header><section className="grid"><section className="card"><h2>{t("PersonalTasks.finished")}</h2><TaskList tasks={finished} empty="PersonalTasks.noFinished" t={t} update={update} /></section><section className="card"><h2>{t("PersonalTasks.archived")}</h2><TaskList tasks={archived} empty="PersonalTasks.noArchived" t={t} update={update} /></section></section></main>;
}
