"use client";

import {useLocale, useTranslations} from "next-intl";

export default function LanguageSwitcher() {
  const locale = useLocale();
  const t = useTranslations("Language");

  function changeLocale(nextLocale) {
    document.cookie = `locale=${nextLocale}; path=/; max-age=31536000; samesite=lax`;
    window.location.reload();
  }

  return <nav className="language-switcher" aria-label={t("label")}>
    {[["en", "EN"], ["uk", "UA"]].map(([code, label]) => <button className={locale === code ? "active" : ""} key={code} type="button" onClick={() => changeLocale(code)}>{label}</button>)}
  </nav>;
}
