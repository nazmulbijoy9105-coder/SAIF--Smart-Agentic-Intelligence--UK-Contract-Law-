"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signIn } from "../../../lib/supabase";
import { LogIn, Loader2 } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const { data, error } = await signIn(email, password);
    setLoading(false);
    if (error) {
      setError(error.message);
    } else if (data.session) {
      localStorage.setItem("saif_token", data.session.access_token);
      router.push("/dashboard");
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">Welcome Back</h1>
          <p className="text-slate-400 mt-2">Sign in to access your assessments</p>
        </div>
        <div className="bg-slate-900 border border-slate-700/50 rounded-xl p-6 shadow-lg">
          {error && <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-sm text-red-300">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Email</label>
              <input type="email" className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Password</label>
              <input type="password" className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <button type="submit" disabled={loading} className="w-full px-6 py-3 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
              Sign In
            </button>
          </form>
          <p className="text-center text-slate-400 text-sm mt-4">
            Don&apos;t have an account? <Link href="/auth/register" className="text-sky-400 hover:text-sky-300">Register</Link>
          </p>
        </div>
      </div>
    </main>
  );
}
