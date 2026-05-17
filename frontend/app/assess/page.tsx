"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { assess } from "@/lib/api";

export default function AssessPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    claimant: "",
    defendant: "",
    contractType: "Commercial",
    contractCategory: "B2B",
    value: "",
    narrative: "",
    disputedClause: "",
    bargainingPower: "equal",
    noticeAdequate: true,
    standardForm: false,
    consumerVulnerable: false,
    allowsUnilateralVariation: false,
    phase: 1,
  });

  useEffect(() => {
    if (!localStorage.getItem("saif_token")) {
      router.push("/auth/login");
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await assess.analyze({
        ...form,
        value: form.value ? parseFloat(form.value) : undefined,
      });
      sessionStorage.setItem("saif_result", JSON.stringify(result));
      router.push("/result");
    } catch (err: any) {
      setError(err.message || "Assessment failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen px-6 py-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-2">ILRMF Assessment</h1>
        <p className="text-white/40">Facts → Law → Argument → Relief</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-red-300 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Parties */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Claimant *</label>
            <input
              value={form.claimant}
              onChange={(e) => setForm({ ...form, claimant: e.target.value })}
              className="premium-input"
              placeholder="Claimant name"
              required
              minLength={2}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Defendant *</label>
            <input
              value={form.defendant}
              onChange={(e) => setForm({ ...form, defendant: e.target.value })}
              className="premium-input"
              placeholder="Defendant name"
              required
              minLength={2}
            />
          </div>
        </div>

        {/* Contract Details */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Type</label>
            <select
              value={form.contractType}
              onChange={(e) => setForm({ ...form, contractType: e.target.value })}
              className="premium-input"
            >
              <option>Commercial</option>
              <option>Employment</option>
              <option>Consumer</option>
              <option>Tenancy</option>
              <option>Service</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Category</label>
            <select
              value={form.contractCategory}
              onChange={(e) => setForm({ ...form, contractCategory: e.target.value })}
              className="premium-input"
            >
              <option value="B2B">B2B</option>
              <option value="B2C">B2C</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Value (£)</label>
            <input
              type="number"
              value={form.value}
              onChange={(e) => setForm({ ...form, value: e.target.value })}
              className="premium-input"
              placeholder="Optional"
            />
          </div>
        </div>

        {/* Narrative */}
        <div>
          <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">
            Narrative & Facts *
          </label>
          <textarea
            value={form.narrative}
            onChange={(e) => setForm({ ...form, narrative: e.target.value })}
            className="premium-input min-h-[150px] resize-y"
            required
            minLength={20}
            placeholder="Describe the dispute, timeline, and key facts..."
          />
        </div>

        {/* Disputed Clause */}
        <div>
          <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Disputed Clause</label>
          <textarea
            value={form.disputedClause}
            onChange={(e) => setForm({ ...form, disputedClause: e.target.value })}
            className="premium-input min-h-[80px] resize-y"
            placeholder="Paste the specific clause in dispute (optional)"
          />
        </div>

        {/* FJR Context */}
        <div className="glass-card">
          <h3 className="font-semibold mb-4 text-sm tracking-tight">FJR Triple-Gate Context</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Bargaining Power</label>
              <select
                value={form.bargainingPower}
                onChange={(e) => setForm({ ...form, bargainingPower: e.target.value })}
                className="premium-input"
              >
                <option value="equal">Equal</option>
                <option value="claimant_weaker">Claimant Weaker</option>
                <option value="defendant_weaker">Defendant Weaker</option>
                <option value="significant_imbalance">Significant Imbalance</option>
              </select>
            </div>
            <div className="space-y-3 pt-6">
              {[
                { key: "noticeAdequate", label: "Notice Adequate" },
                { key: "standardForm", label: "Standard Form Contract" },
                { key: "consumerVulnerable", label: "Consumer Vulnerable" },
                { key: "allowsUnilateralVariation", label: "Unilateral Variation Clause" },
              ].map((item) => (
                <label key={item.key} className="flex items-center gap-3 text-sm text-white/60 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form[item.key as keyof typeof form] as boolean}
                    onChange={(e) => setForm({ ...form, [item.key]: e.target.checked })}
                    className="w-4 h-4 rounded border-white/20 bg-white/5 accent-blue-500"
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full py-4 text-lg"
        >
          {loading ? "Running ILRMF Analysis..." : "Run ILRMF Assessment"}
        </button>
      </form>
    </main>
  );
}
