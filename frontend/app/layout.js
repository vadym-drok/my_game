import "./globals.css";
import {NextIntlClientProvider} from "next-intl";
import {getLocale, getTranslations} from "next-intl/server";
import LanguageSwitcher from "./language-switcher";

export async function generateMetadata() {
  const t = await getTranslations();
  return {
    title: t("Home.title"),
    description: t("Metadata.description"),
    icons: { icon: "/images/general/game_logo.png" },
  };
}

export default async function RootLayout({ children }) {
  const locale = await getLocale();
  return (
    <html lang={locale}>
      <body><NextIntlClientProvider><LanguageSwitcher />{children}</NextIntlClientProvider></body>
    </html>
  );
}
