import {getRequestConfig} from "next-intl/server";
import {cookies} from "next/headers";

const locales = ["en", "uk"];

export default getRequestConfig(async () => {
  const locale = (await cookies()).get("locale")?.value;
  const resolvedLocale = locales.includes(locale) ? locale : "en";
  return {
    locale: resolvedLocale,
    messages: (await import(`../messages/${resolvedLocale}.json`)).default,
  };
});
