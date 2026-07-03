import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Momentum 360 Agents",
  description: "Ask anything about growing your business — powered by Momentum 360 and Fable 5.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
