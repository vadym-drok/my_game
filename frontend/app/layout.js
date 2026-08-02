import "./globals.css";

export const metadata = {
  title: "My Game",
  description: "Nation simulator",
};

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  );
}
