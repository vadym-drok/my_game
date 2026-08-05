"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";

export default function AppNav() {
  const t = useTranslations("Nav");
  const pathname = usePathname();
  const links = [["/nations", "nations"], ["/", "overview"], ["/buildings", "buildings"]];
  return <nav className="app-nav" aria-label="Main navigation">{links.map(([href, label]) => <Link key={href} className={pathname === href ? "active" : ""} href={href}>{t(label)}</Link>)}</nav>;
}
