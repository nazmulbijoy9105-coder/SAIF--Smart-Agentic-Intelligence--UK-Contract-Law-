"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { exportToPDF } from "@/lib/pdf-export";

export default function ResultPage() {
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("saif_result");
    if (!stored) {
      window.location.href = "/assess";
      return;
    }
    setResult(JSON.parse(stored));
  }, []);

  if (!result) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-white/40">Loading...</div>
      </main>
    );
  }

  const data = result.data || {};
  const facts = data.facts || {};
  const issues = data.issues || [];
  const relief = data.relief || {};
  const governance = data.governance || {};

  return (
    <main className="min-h-screen px-6 py-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-10">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">ILRMF Result</h1>
          <p className="text-white/30 text-sm mt-1">
            ID: {result.assessment_id} · Phase {result.phase}
          </p>
        </div>
        <button
          onClick={() => exportToPDF({ ...data, assessment_id: result.assessment_id })}
          className="btn-secondary text-sm"
        >
          Export Report
        </button>
      </div>

      {/* Governance Banner */}
      <div className={`glass-card mb-6 border-l-4 ${
        governance.hallucination === "ZERO" ? "border-l-green-400" : "border-l-red-400"
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-white/40 uppercase tracking-wider">Hallucination Status</span>
            <p className={`text-lg font-bold mt-1 ${
              governance.hallucination === "ZERO" ? "text-green-400" : "text-red-400"
            }`}>
              {governance.hallucination === "ZERO" ? "✓ ZERO" : "✗ FLAGGED"}
            </p>
          </div>
          <div className="text-right text-xs text-white/30">
            {governance.citationValidation && (
              <>
                <div>Verified: {governance.citationValidation.verified_count || 0}</div>
                <div>Flagged: {governance.citationValidation.flagged_count || 0}</div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Facts */}
      <div className="glass-card mb-6">
        <h2 className="text-lg font-semibold mb-4 tracking-tight">Facts</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div><span className="text-white/40">Parties:</span> <span className="text-white/80">{facts.parties || "N/A"}</span></div>
          <div><span className="text-white/40">Type:</span> <span className="text-white/80">{facts.contractType || "N/A"}</span></div>
          <div><span className="text-white/40">Category:</span> <span className="text-white/80">{facts.consumerType || "N/A"}</span></div>
          <div><span className="text-white/40">Value:</span> <span className="text-white/80">{facts.value || "N/A"}</span></div>
          <div><span className="text-white/40">Bargaining:</span> <span className="text-white/80">{facts.bargainingPower || "N/A"}</span></div>
          <div><span className="text-white/40">Standard Form:</span> <span className="text-white/80">{facts.standardForm ? "Yes" : "No"}</span></div>
        </div>
        {facts.disputedClause && (
          <div className="mt-4 p-4 bg-orange-500/5 border border-orange-500/10 rounded-xl text-sm">
            <span className="text-orange-300 font-medium">Disputed Clause:</span>{" "}
            <span className="text-white/60">{facts.disputedClause}</span>
          </div>
        )}
      </div>

      {/* Issues & FJR */}
      <h2 className="text-lg font-semibold mb-4 tracking-tight">
        Issues & FJR Triple-Gate ({issues.length})
      </h2>

      {issues.length === 0 ? (
        <div className="glass-card text-center py-8 text-white/30">
          No issues identified — the contract appears compliant.
        </div>
      ) : (
        issues.map((issue: any, idx: number) => {
          const fjr = issue.fjr || {};
          const score = fjr.score || 0;
          const scoreColor = score >= 70 ? "text-green-400" : score >= 40 ? "text-orange-400" : "text-red-400";

          return (
            <div key={idx} className="glass-card mb-4">
              {/* Issue Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg tracking-tight">Issue {idx + 1}</h3>
                  <p className="text-white/50 text-sm mt-1">{issue.issue}</p>
                </div>
                <div className="text-4xl font-bold font-mono ml-4">
                  <span className={scoreColor}>{score}</span>
                  <span className="text-white/20 text-lg">/100</span>
                </div>
              </div>

              {/* Law */}
              <div className="p-4 bg-white/[0.02] rounded-xl text-sm mb-4 border border-white/[0.04]">
                <span className="text-white/40 font-medium">Law: </span>
                <span className="text-white/70">{issue.law || "Not specified"}</span>
              </div>

              {/* FJR Gates */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className={fjr.fair ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-white/40 uppercase tracking-wider">Fair</div>
                  <div className={`text-xl font-bold ${fjr.fair ? "text-green-400" : "text-red-400"}`}>
                    {fjr.fair ? "✓" : "✗"}
                  </div>
                  {fjr.fairScore !== undefined && (
                    <div className="text-[10px] text-white/30">{fjr.fairScore}/100</div>
                  )}
                </div>
                <div className={fjr.just ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-white/40 uppercase tracking-wider">Just</div>
                  <div className={`text-xl font-bold ${fjr.just ? "text-green-400" : "text-red-400"}`}>
                    {fjr.just ? "✓" : "✗"}
                  </div>
                  {fjr.justScore !== undefined && (
                    <div className="text-[10px] text-white/30">{fjr.justScore}/100</div>
                  )}
                </div>
                <div className={fjr.reasonable ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-white/40 uppercase tracking-wider">Reasonable</div>
                  <div className={`text-xl font-bold ${fjr.reasonable ? "text-green-400" : "text-red-400"}`}>
                    {fjr.reasonable ? "✓" : "✗"}
                  </div>
                  {fjr.reasonableScore !== undefined && (
                    <div className="text-[10px] text-white/30">{fjr.reasonableScore}/100</div>
                  )}
                </div>
              </div>

              {/* Arguments */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded-xl">
                  <div className="text-blue-400 text-xs font-semibold mb-1 uppercase tracking-wider">Claimant</div>
                  <p className="text-sm text-white/60">{issue.argument?.claimant || "N/A"}</p>
                </div>
                <div className="p-4 bg-purple-500/5 border border-purple-500/10 rounded-xl">
                  <div className="text-purple-400 text-xs font-semibold mb-1 uppercase tracking-wider">Defendant</div>
                  <p className="text-sm text-white/60">{issue.argument?.defendant || "N/A"}</p>
                </div>
              </div>

              {/* Verdict */}
              <div className={`p-4 rounded-xl text-sm font-medium ${
                issue.verdict?.includes("ENFORCEABLE")
                  ? "bg-green-500/8 text-green-300 border border-green-500/15"
                  : issue.verdict?.includes("VOID") && !issue.verdict?.includes("LIKELY")
                  ? "bg-red-500/8 text-red-300 border border-red-500/15"
                  : "bg-orange-500/8 text-orange-300 border border-orange-500/15"
              }`}>
                {issue.verdict || "Not assessed"}
              </div>
            </div>
          );
        })
      )}

      {/* Relief */}
      <div className="glass-card mb-6">
        <h2 className="text-lg font-semibold mb-4 tracking-tight">Relief & Remedies</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-white/40">Primary:</span>{" "}
            <span className="text-white/80">{relief.primary || "N/A"}</span>
          </div>
          <div>
            <span className="text-white/40">Damages:</span>{" "}
            <span className="text-white/80">{relief.damages || "N/A"}</span>
          </div>
          <div>
            <span className="text-white/40">Court:</span>{" "}
            <span className="text-white/80">{relief.court || "N/A"}</span>
          </div>
          <div>
            <span className="text-white/40">Probability:</span>{" "}
            <span className="text-white/80">{relief.probability || 0}%</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-4 mb-8">
        <Link href="/assess" className="btn-primary">
          New Assessment
        </Link>
        <Link href="/dashboard" className="btn-secondary">
          Dashboard
        </Link>
      </div>

      <p className="text-center text-xs text-white/15">
        ILRMF Engine v1.0 — AI-assisted analysis. Not legal advice. Consult a qualified solicitor.
      </p>
    </main>
  );
}
