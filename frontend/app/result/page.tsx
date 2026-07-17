"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { exportToPDF } from "@/lib/pdf-export";

export default function ResultPage() {
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("saif_result");
      window.location.href = "/assess";
      return;
    }
    setResult(JSON.parse(stored));
  }, []);

    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </main>
    );
  }

  const data = result.data || {};
  const facts = data.facts || {};
  const issues = data.issues || [];
  const relief = data.relief || {};
  const governance = data.governance || {};
  const warnings = governance.applicationWarnings || [];
  const citationStatus = governance.citationStatus || "UNKNOWN";

  const badgeConfig: Record<string, { label: string; color: string; bg: string; border: string }> = {
    NAMES_VERIFIED: { label: "CITATION NAMES VERIFIED", color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/30" },
    NAMES_VERIFIED_APPLICATION_FLAGGED: { label: "CITATIONS VERIFIED — APPLICATION FLAGGED", color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/30" },
    FLAGS_FOUND: { label: "UNKNOWN CITATIONS DETECTED", color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30" },
    UNKNOWN: { label: "NOT VALIDATED", color: "text-gray-400", bg: "bg-gray-500/10", border: "border-gray-500/30" },
    PARSE_ERROR: { label: "RESPONSE ERROR", color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30" },
  };

  const badge = badgeConfig[citationStatus] || badgeConfig.UNKNOWN;

  return (
    <main className="min-h-screen px-6 py-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-10">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">ILRMF Result</h1>
          <p className="text-gray-400 text-sm mt-1">
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

      {/* HONEST Citation Status Banner */}
      <div className={\}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Citation Status</span>
            <p className={\}>
              {badge.label}
            </p>
          </div>
          <div className="text-right text-xs text-gray-400">
            {governance.citationValidation && (
              <>
                <div>Known: {governance.citationValidation.verified_count || 0}</div>
                <div>Unknown: {governance.citationValidation.flagged_count || 0}</div>
              </>
            )}
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2 leading-relaxed">
          {citationStatus === "NAMES_VERIFIED"
            ? "Case names match known UK cases. NOTE: This does NOT verify that cases are correctly applied to these facts. AI-assisted analysis — consult a solicitor."
            : citationStatus === "NAMES_VERIFIED_APPLICATION_FLAGGED"
            ? governance.citationDetail
            : "Citations could not be fully validated. Exercise extreme caution."}
        </p>
      </div>

      {/* Application Warnings */}
      {warnings.length > 0 && (
        <div className="glass-card mb-4 border-l-4 border-orange-500/50 bg-orange-500/5">
          <span className="text-xs font-bold text-orange-400 uppercase tracking-wider">Application Warnings</span>
          <ul className="mt-2 space-y-1">
            {warnings.map((w: string, i: number) => (
              <li key={i} className="text-sm text-orange-300/80">⚠ {w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* DISCLAIMER */}
      <div className="glass-card mb-6 bg-red-500/5 border border-red-500/15">
        <p className="text-xs text-red-300/80 leading-relaxed">
          <strong>NOT LEGAL ADVICE.</strong> This is AI-assisted analysis using pattern-matching, not legal reasoning.
          Case citations are name-checked only — correct application to facts is NOT validated.
          Damages figures, probability scores, and remedy suggestions may be incorrect.
          Always consult a qualified solicitor before making legal decisions.
        </p>
      </div>

      {/* Facts */}
      <div className="glass-card mb-6">
        <h2 className="text-lg font-semibold mb-4 tracking-tight">Facts</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div><span className="text-gray-400">Parties:</span> <span className="text-gray-700">{facts.parties || "N/A"}</span></div>
          <div><span className="text-gray-400">Type:</span> <span className="text-gray-700">{facts.contractType || "N/A"}</span></div>
          <div><span className="text-gray-400">Category:</span> <span className="text-gray-700">{facts.consumerType || "N/A"}</span></div>
          <div><span className="text-gray-400">Value:</span> <span className="text-gray-700">{facts.value || "N/A"}</span></div>
          <div><span className="text-gray-400">Bargaining:</span> <span className="text-gray-700">{facts.bargainingPower || "N/A"}</span></div>
          <div><span className="text-gray-400">Standard Form:</span> <span className="text-gray-700">{facts.standardForm ? "Yes" : "No"}</span></div>
        </div>
        {facts.disputedClause && (
          <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-xl text-sm">
            <span className="text-orange-600 font-medium">Disputed Clause:</span>{" "}
            <span className="text-gray-600">{facts.disputedClause}</span>
          </div>
        )}
      </div>

      {/* Issues & FJR */}
      <h2 className="text-lg font-semibold mb-4 tracking-tight">
        Issues & FJR Triple-Gate ({issues.length})
      </h2>

      {issues.length === 0 ? (
        <div className="glass-card text-center py-8 text-gray-400">
          No issues identified.
        </div>
      ) : (
        issues.map((issue: any, idx: number) => {
          const fjr = issue.fjr || {};
          const score = fjr.score || 0;
          const scoreColor = score >= 70 ? "text-green-600" : score >= 40 ? "text-orange-500" : "text-red-500";

          return (
            <div key={idx} className="glass-card mb-4">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg tracking-tight">Issue {idx + 1}</h3>
                  <p className="text-gray-500 text-sm mt-1">{issue.issue}</p>
                </div>
                <div className="text-4xl font-bold font-mono ml-4">
                  <span className={scoreColor}>{score}</span>
                  <span className="text-gray-300 text-lg">/100</span>
                </div>
              </div>

              {/* Law */}
              <div className="p-4 bg-gray-50 rounded-xl text-sm mb-4 border border-gray-200">
                <span className="text-amber-600 font-semibold text-xs uppercase tracking-wider">Law: </span>
                <span className="text-gray-700 leading-relaxed">{issue.law || "Not specified"}</span>
              </div>

              {/* FJR Gates */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className={fjr.fair ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">Fair</div>
                  <div className={\}>
                    {fjr.fair ? "✓" : "✗"}
                  </div>
                  {fjr.fairScore !== undefined && (
                    <div className="text-[10px] text-gray-400">{fjr.fairScore}/100</div>
                  )}
                </div>
                <div className={fjr.just ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">Just</div>
                  <div className={\}>
                    {fjr.just ? "✓" : "✗"}
                  </div>
                  {fjr.justScore !== undefined && (
                    <div className="text-[10px] text-gray-400">{fjr.justScore}/100</div>
                  )}
                </div>
                <div className={fjr.reasonable ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">Reasonable</div>
                  <div className={\}>
                    {fjr.reasonable ? "✓" : "✗"}
                  </div>
                  {fjr.reasonableScore !== undefined && (
                    <div className="text-[10px] text-gray-400">{fjr.reasonableScore}/100</div>
                  )}
                </div>
              </div>

              {/* FJR Analysis */}
              {fjr.analysis && (
                <div className="p-4 bg-gray-50 rounded-xl text-sm mb-4 border border-gray-200">
                  <span className="text-gray-500 font-semibold text-xs uppercase tracking-wider">FJR Analysis: </span>
                  <p className="text-gray-600 leading-relaxed mt-1 whitespace-pre-line">{fjr.analysis}</p>
                </div>
              )}

              {/* Arguments */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <div className="text-blue-600 text-xs font-bold mb-2 uppercase tracking-wider">Claimant Argument</div>
                  <p className="text-sm text-gray-700 leading-relaxed">{issue.argument?.claimant || "N/A"}</p>
                </div>
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl">
                  <div className="text-purple-600 text-xs font-bold mb-2 uppercase tracking-wider">Defendant Argument</div>
                  <p className="text-sm text-gray-700 leading-relaxed">{issue.argument?.defendant || "N/A"}</p>
                </div>
              </div>

              {/* Verdict */}
              <div className={\}>
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
            <span className="text-gray-400">Primary:</span>{" "}
            <span className="text-gray-700">{relief.primary || "N/A"}</span>
          </div>
          <div>
            <span className="text-gray-400">Damages:</span>{" "}
            <span className="text-gray-700">{relief.damages || "N/A"}</span>
          </div>
          <div>
            <span className="text-gray-400">Court:</span>{" "}
            <span className="text-gray-700">{relief.court || "N/A"}</span>
          </div>
          <div>
            <span className="text-gray-400">Probability:</span>{" "}
            <span className="text-gray-700">{relief.probability || 0}%</span>
          </div>
        </div>
        {relief.reasoning && (
          <p className="text-xs text-gray-400 mt-3 leading-relaxed">Methodology: {relief.reasoning}</p>
        )}
      </div>

      {/* Navigation */}
      <div className="flex gap-4 mb-8">
        <Link href="/assess" className="btn-primary">New Assessment</Link>
        <Link href="/dashboard" className="btn-secondary">Dashboard</Link>
      </div>

      <p className="text-center text-xs text-red-400/60 font-medium">
        ILRMF Engine v1.0 — NOT LEGAL ADVICE. AI pattern-matching is not a substitute for legal expertise. Consult a solicitor.
      </p>
    </main>
  );
}
