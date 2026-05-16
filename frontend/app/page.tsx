import Link from 'next/link';
export default function Home() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
            <div className="text-blue-400 text-sm font-mono tracking-widest mb-4">ILRMF Engine v1.0 — NB TECH</div>
            <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">SAIF</h1>
            <p className="text-xl text-gray-300 mb-8">Smart Agentic Intelligence Framework — UK Contract Law AI</p>
            <div className="flex gap-4">
                <Link href="/assess" className="saif-btn saif-btn-primary px-8 py-3 text-lg">Start Assessment</Link>
                <Link href="/pricing" className="saif-btn saif-btn-secondary px-8 py-3 text-lg">View Plans</Link>
            </div>
            <p className="mt-12 text-xs text-gray-500">Created by Md Nazmul Islam (Bijoy) — Advocate, Supreme Court of Bangladesh</p>
        </main>
    );
}
