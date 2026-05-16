import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'SAIF — UK Contract Law AI' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (<html lang="en"><body className="min-h-screen bg-[var(--bg)] antialiased">{children}</body></html>);
}
