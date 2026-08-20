'use client';

import Link from 'next/link';
import { Scale, Shield, Brain, FileText, ArrowRight, CheckCircle } from 'lucide-react';

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-legal-dark to-legal-panel py-24 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-saif-500/10 border border-saif-500/30 rounded-full px-4 py-1.5 text-saif-300 text-sm font-medium mb-8">
            <Shield className="w-4 h-4" />
            ILRMF v3.0 Dual-Predicate Architecture
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
            SAIF
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-4 font-serif">
            Smart Agentic Intelligence Framework
          </p>
          <p className="text-gray-400 max-w-2xl mx-auto mb-10">
            AI-powered UK Contract Law analysis with zero-hallucination guardrails. 
            Assess B2B, B2C, Employment, and Tenancy disputes with deterministic 
            Fair-Just-Reasonable triple-gate scoring.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/assess" className="saif-btn-primary inline-flex items-center gap-2 text-lg">
              <Brain className="w-5 h-5" />
              Start Assessment
            </Link>
            <Link href="/auth/login" className="saif-btn-outline inline-flex items-center gap-2 text-lg">
              <FileText className="w-5 h-5" />
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-legal-dark">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-white mb-16">
            Engineered for Legal Precision
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Scale className="w-8 h-8 text-saif-400" />}
              title="Dual-Predicate Analysis"
              description="Separates subjective client belief from objective legal status, surfacing divergence penalties where perception does not match reality."
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8 text-legal-gold" />}
              title="Zero Hallucination"
              description="FJR Triple-Gate and Citation Checker validate every case reference against the verified Phase-1 corpus before delivery."
            />
            <FeatureCard
              icon={<Brain className="w-8 h-8 text-saif-400" />}
              title="Domain Routing"
              description="Automatic classification into Commercial, Consumer, Employment, or Tenancy modes with statute-specific routing directives."
            />
          </div>
        </div>
      </section>

      {/* Domains */}
      <section className="py-20 px-4 bg-legal-panel">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-white mb-12">Supported Domains</h2>
          <div className="grid sm:grid-cols-2 gap-6">
            <DomainCard
              title="Commercial / B2B"
              statutes="UCTA 1977, Late Payment of Commercial Debts Act 1998"
              cases="Photo Production v Securicor, Regus v Epcot"
            />
            <DomainCard
              title="Consumer / B2C"
              statutes="CRA 2015, Consumer Contracts Regulations 2013"
              cases="DGFT v First National Bank, Smith v Eric S Bush"
            />
            <DomainCard
              title="Employment"
              statutes="ERA 1996, Equality Act 2010"
              cases="British Home Stores v Burchell, Polkey v AEA"
            />
            <DomainCard
              title="Landlord & Tenant"
              statutes="LTA 1985, Housing Act 2004"
              cases="Liverpool CC v Irwin, Southwark LBC v Mills"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-800 text-center text-gray-500 text-sm">
        <p>© 2024 SAIF by Md Nazmul Islam (Bijoy) | NB TECH Bangladesh</p>
        <p className="mt-1">ILRMF v3.0 — Not legal advice. For educational and analytical purposes only.</p>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="saif-card hover:border-saif-500/30 transition-colors">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-gray-400 leading-relaxed">{description}</p>
    </div>
  );
}

function DomainCard({ title, statutes, cases }: { title: string; statutes: string; cases: string }) {
  return (
    <div className="saif-card">
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <div className="space-y-2 text-sm">
        <div className="flex items-start gap-2">
          <CheckCircle className="w-4 h-4 text-saif-400 mt-0.5 shrink-0" />
          <span className="text-gray-300"><span className="text-gray-500">Statutes:</span> {statutes}</span>
        </div>
        <div className="flex items-start gap-2">
          <CheckCircle className="w-4 h-4 text-legal-gold mt-0.5 shrink-0" />
          <span className="text-gray-300"><span className="text-gray-500">Cases:</span> {cases}</span>
        </div>
      </div>
    </div>
  );
}
