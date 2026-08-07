"use client";

import { useTranslations } from "next-intl";
import { ICON_SIZES } from "../../app/settings";
import GameIconFrame from "../game-art/GameIconFrame";

export default function ItemIcon({ item, type = "resource" }) {
  const t = useTranslations("Data");
  const category = type === "work_type" ? "workTypes" : type === "building" || type === "building_detail" ? "buildings" : "resources";
  const key = `${category}.${item.code}`;
  const name = t.has(key) ? t(key) : item.name || item.code;
  return <span className="icon-tooltip tooltip" data-tooltip={name} tabIndex="0"><GameIconFrame src={item.image_path} alt={name} code={item.code} size={ICON_SIZES[type]} /></span>;
}
