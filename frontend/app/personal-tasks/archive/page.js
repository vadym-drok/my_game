"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function TaskList({ tasks, empty, t }) {
  return tasks.length === 0 ? <p>{t(empty)}</p> : <ul className="personal-tasks">{tasks.map((task) => <li key={task.id} className={task.status === "cancelled" && task.counter > 0 ? "was-completed" : ""}><div className="task-info"><strong>{task.name}</strong><span>{t(`PersonalTaskTypes.${task.task_type}`)} · {t("PersonalTasks.reward")}: {task.reward}{task.status === "cancelled" && ` (${t("PersonalTasks.completedCount", { count: task.counter })})`}</span><p>{task.description}</p></div></li>)}</ul>;
}

export default function PersonalTaskArchivePage() {
  const t = useTranslations(); const router = useRouter(); const [tasks, setTasks] = useState([]);
  useEffect(() => { const nationId = window.localStorage.getItem("nationId"); if (!nationId) return router.replace("/nations"); fetch(`${API_URL}/nations/${nationId}/personal-tasks`).then((response) => response.json()).then(setTasks); }, []);
  const finished = tasks.filter((task) => task.status === "done" && task.task_type === "one_time"); const archived = tasks.filter((task) => task.status === "cancelled");
  return <main><header className="page-header"><div><p className="eyebrow">{t("Common.nationSimulator")}</p><h1>{t("PersonalTasks.archiveTitle")}</h1></div><Link className="page-link" href="/personal-tasks">{t("PersonalTasks.back")}</Link></header><section className="grid"><section className="card"><h2>{t("PersonalTasks.finished")}</h2><TaskList tasks={finished} empty="PersonalTasks.noFinished" t={t} /></section><section className="card"><h2>{t("PersonalTasks.archived")}</h2><TaskList tasks={archived} empty="PersonalTasks.noArchived" t={t} /></section></section></main>;
}
