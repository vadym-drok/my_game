import "./globals.css";
import "./branding.css";
import {NextIntlClientProvider} from "next-intl";
import {getLocale} from "next-intl/server";
import LanguageSwitcher from "./language-switcher";
import GameShell from "../components/layout/GameShell";

export const metadata = { icons: { icon: "/images/general/game_logo.png" } };

export default async function RootLayout({ children }) {
  const locale = await getLocale();
  return (
    <html lang={locale}>
      <body><NextIntlClientProvider><GameShell actions={<LanguageSwitcher />}>{children}</GameShell></NextIntlClientProvider></body>
    </html>
  );
}
