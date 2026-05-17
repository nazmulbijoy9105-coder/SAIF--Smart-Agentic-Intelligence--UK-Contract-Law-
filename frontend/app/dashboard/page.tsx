"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { assess, payment } from "@/lib/api";

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [credits, setCredits] = useState(0);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("saif_user");
    if (!stored) {
      window.location.href = "/auth/login";
      return;
    }
    setUser(JSON.parse(stored));
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [creditsData, historyData] = await Promise.all([
        payment.credits().catch(() => ({ credits_remaining: 0 })),
        assess.history().catch(() => ({ data: [] })),
      ]);
      setCredits(creditsData.credits_remaining || 0);
      setHistory(historyData.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("saif_token");
    localStorage.removeItem("saif_user");
    window.location.href = "/";
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-white/40">Loading...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-white/40 mt-1">{user?.email} — ILRMF v1.0</p>
        </div>
        <div className="flex gap-3">
          <Link href="/assess" className="btn-primary px-6">
            New Assessment
          </Link>
          <button onClick={handleLogout} className="btn-secondary px-6">
            Sign Out
          </button>
        </div>
      </div>

      {/* Credits Card */}
      <div className="glass-card mb-8 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-white/40 uppercase tracking-wider mb-1">Credits Remaining</p>
          <p className="text-sm text-white/50">Each assessment uses 1 credit</p>
        </div>
        <div className="text-5xl font-bold gradient-text-blue">{credits}</div>
        {credits <= 1 && (
          <Link href="/pricing" className="btn-primary text-sm px-5 py-2.5">
            Get Credits
          </Link>
        )}
      </div>

      {/* History */}
      <h2 className="text-xl font-semibold mb-4 tracking-tight">Assessment History</h2>
      {history.length === 0 ? (
        <div className="glass-card text-center py-12">
          <p className="text-white/30 mb-4">No assessments yet</p>
          <Link href="/assess" className="btn-primary">
            Start your first assessment
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item: any) => (
            <div key={item.id} className="glass-card flex items-center justify-between py-4">
              <div>
                <p className="font-medium">{item.contract_type || "Assessment"}</p>
                <p className="text-sm text-white/30">
                  {new Date(item.created_at).toLocaleDateString("en-GB", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                  {" · "}
                  {item.court_track || "N/A"}
                </p>
              </div>
              <span className={`text-sm font-mono ${
                (item.overall_risk_score || 0) >= 60
                  ? "text-green-400"
                  : "text-orange-400"
              }`}>
                {item.overall_risk_score || "—"}
              </span>
            </div>
          ))}
        </div>
      )}

      <p className="mt-12 text-center text-xs text-white/15">
        ILRMF Engine v1.0 — Md Nazmul Islam (Bijoy) — NB TECH Bangladesh
      </p>
    </main>
  );
}
