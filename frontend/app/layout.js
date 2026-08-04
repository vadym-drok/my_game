import "./globals.css";

export const metadata = {
  title: "My Game",
  description: "Nation simulator",
  icons: { icon: "/images/general/game_logo.png" },
};

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  );
}
