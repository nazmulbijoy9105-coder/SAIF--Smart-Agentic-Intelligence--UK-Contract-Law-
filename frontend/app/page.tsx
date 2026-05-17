import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-purple-500/8 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 text-center max-w-3xl animate-in">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 mb-8">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs font-medium text-white/60 tracking-wide">
            ILRMF Engine v1.0 — NB TECH Bangladesh
          </span>
        </div>

        {/* Title */}
        <h1 className="text-7xl md:text-8xl font-bold tracking-tight mb-6 gradient-text">
          SAIF
        </h1>

        <p className="text-xl md:text-2xl text-white/70 font-light mb-2 tracking-tight">
          Smart Agentic Intelligence Framework
        </p>

        <p className="text-lg text-white/40 font-light mb-12">
          UK Contract Law AI — Fair · Just · Reasonable
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Link href="/assess" className="btn-primary text-lg px-10 py-4">
            Start Assessment
          </Link>
          <Link href="/pricing" className="btn-secondary text-lg px-10 py-4">
            View Plans
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 max-w-md mx-auto">
          <div>
            <div className="text-3xl font-bold gradient-text-blue">ZERO</div>
            <div className="text-xs text-white/40 mt-1 uppercase tracking-wider">Hallucination</div>
          </div>
          <div>
            <div className="text-3xl font-bold gradient-text-blue">FJR</div>
            <div className="text-xs text-white/40 mt-1 uppercase tracking-wider">Triple-Gate</div>
          </div>
          <div>
            <div className="text-3xl font-bold gradient-text-blue">4</div>
            <div className="text-xs text-white/40 mt-1 uppercase tracking-wider">Court Tracks</div>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-16 text-xs text-white/20">
          Created by Md Nazmul Islam (Bijoy) — Advocate, Supreme Court of Bangladesh
        </p>
      </div>
    </main>
  );
}
