"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { ICON_SIZES } from "../../app/settings";

export default function ItemIcon({ item, type = "resource" }) {
  const t = useTranslations("Data");
  const [missing, setMissing] = useState(!item.image_path);
  const category = type === "work_type" ? "workTypes" : type === "building" || type === "building_detail" ? "buildings" : "resources";
  const key = `${category}.${item.code}`;
  const name = t.has(key) ? t(key) : item.name || item.code;
  return <span className={`icon-tooltip tooltip icon-frame ${item.icon_frame_image_path ? "has-frame" : ""}`} style={{ "--icon-size": `${ICON_SIZES[type]}px`, "--icon-frame": `url(${item.icon_frame_image_path})` }} data-tooltip={name} tabIndex="0">{missing ? <span className="game-icon fallback">{item.code}</span> : <img className="game-icon" src={item.image_path} alt={name} onError={() => setMissing(true)} />}</span>;
}
