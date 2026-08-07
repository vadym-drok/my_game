"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Building2, ClipboardList, Globe2, Hammer, Landmark, MapPinned, Package } from "lucide-react";
import { useTranslations } from "next-intl";

const links = [
  ["/", "overview", Landmark],
  ["/nations", "nations", Globe2],
  ["/processes", "processes", Hammer],
  ["/buildings", "buildings", Building2],
  ["/locations", "locations", MapPinned],
  ["/items", "items", Package],
  ["/personal-tasks", "personalTasks", ClipboardList],
];

export default function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("Nav");
  return <aside className="game-sidebar">
    <Link className="game-identity" href="/" aria-label={t("overview")}>
      <Image src="/images/general/game_logo.png" alt="" width={58} height={58} priority />
      <span>My Game</span>
    </Link>
    <nav className="sidebar-nav" aria-label="Main navigation">
      {links.map(([href, label, Icon]) => <Link key={href} className={(href === "/" ? pathname === href : pathname.startsWith(href)) ? "active" : ""} href={href}><Icon aria-hidden="true" /><span>{t(label)}</span></Link>)}
    </nav>
  </aside>;
}
