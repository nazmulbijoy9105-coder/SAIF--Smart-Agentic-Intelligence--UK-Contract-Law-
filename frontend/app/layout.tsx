import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SAIF — Smart Agentic Intelligence Framework | UK Contract Law AI',
  description: 'AI-powered UK Contract Law assessment engine. ILRMF v3.0 Dual-Predicate Architecture by Md Nazmul Islam (Bijoy), NB TECH Bangladesh.',
  keywords: 'UK Contract Law, AI Legal, ILRMF, Contract Assessment, UCTA 1977, CRA 2015',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        {children}
      </body>
    </html>
  );
}
