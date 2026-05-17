import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SAIF — UK Contract Law AI",
  description: "Smart Agentic Intelligence Framework — ILRMF Engine",
  keywords: ["UK contract law", "AI legal analysis", "ILRMF", "SAIF"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-black antialiased">
        {children}
      </body>
    </html>
  );
}
