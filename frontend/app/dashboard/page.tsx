"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getUser, signOut } from "../../lib/supabase";
import { LayoutDashboard, Plus, LogOut, CreditCard } from "lucide-react";

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUser().then((u) => { setUser(u); setLoading(false); });
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-slate-400">Loading...</div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-400 mb-4">Please sign in to view your dashboard</p>
          <Link href="/auth/login" className="px-6 py-3 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-medium transition-colors">Sign In</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <LayoutDashboard className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          </div>
          <button onClick={() => { signOut(); window.location.href = "/"; }} className="px-4 py-2 rounded-lg border border-sky-500 text-sky-400 hover:bg-sky-500/10 text-sm font-medium transition-colors flex items-center gap-2">
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>

        <div className="grid sm:grid-cols-3 gap-4 mb-8">
          <div className="bg-slate-900 border border-slate-700/50 rounded-xl p-6 shadow-lg text-center">
            <p className="text-slate-400 text-sm">Available Credits</p>
            <p className="text-3xl font-bold text-sky-400 mt-1">3</p>
          </div>
          <div className="bg-slate-900 border border-slate-700/50 rounded-xl p-6 shadow-lg text-center">
            <p className="text-slate-400 text-sm">Assessments</p>
            <p className="text-3xl font-bold text-white mt-1">0</p>
          </div>
          <div className="bg-slate-900 border border-slate-700/50 rounded-xl p-6 shadow-lg text-center">
            <p className="text-slate-400 text-sm">Account</p>
            <p className="text-sm text-white mt-2 truncate">{user.email}</p>
          </div>
        </div>

        <div className="flex gap-4">
          <Link href="/assess" className="px-6 py-3 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-medium transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" /> New Assessment
          </Link>
          <Link href="/pricing" className="px-6 py-3 rounded-lg border border-sky-500 text-sky-400 hover:bg-sky-500/10 font-medium transition-colors flex items-center gap-2">
            <CreditCard className="w-4 h-4" /> Buy Credits
          </Link>
        </div>
      </div>
    </main>
  );
}
