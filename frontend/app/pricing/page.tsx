"use client";
import { payment } from "@/lib/api";

export default function PricingPage() {
  const handleCheckout = async (plan: string) => {
    if (!localStorage.getItem("saif_token")) {
      window.location.href = "/auth/login";
      return;
    }
    try {
      const r = await payment.checkout(
        plan,
        `${window.location.origin}/dashboard`,
        `${window.location.origin}/pricing`
      );
      if (r.url) window.location.href = r.url;
    } catch (e: any) {
      alert(e.message);
    }
  };

  const plans = [
    {
      id: "free",
      name: "Free",
      price: "£0",
      period: "forever",
      credits: 3,
      cta: "Current Plan",
      disabled: true,
      features: ["3 assessments", "Basic ILRMF analysis", "FJR Triple-Gate"],
      highlight: false,
    },
    {
      id: "pro",
      name: "Pro",
      price: "£19.99",
      period: "/month",
      credits: 50,
      cta: "Upgrade to Pro",
      disabled: false,
      features: [
        "50 assessments/month",
        "Full ILRMF analysis",
        "FJR Triple-Gate scoring",
        "Citation validation",
        "Court track routing",
        "Assessment history",
        "PDF report export",
      ],
      highlight: true,
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: "£99.99",
      period: "/month",
      credits: 999,
      cta: "Contact Sales",
      disabled: false,
      features: [
        "Unlimited assessments",
        "Full ILRMF analysis",
        "API access",
        "Custom integrations",
        "Dedicated support",
        "All phases access",
      ],
      highlight: false,
    },
  ];

  return (
    <main className="min-h-screen px-6 py-16 max-w-5xl mx-auto">
      <div className="text-center mb-14">
        <h1 className="text-5xl font-bold tracking-tight mb-4">Choose Your Plan</h1>
        <p className="text-white/40 text-lg">UK Contract Law AI — Powered by ILRMF Engine</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-14">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`glass-card relative ${
              plan.highlight ? "border-blue-500/30 shadow-[0_0_40px_rgba(41,151,255,0.08)]" : ""
            }`}
          >
            {plan.highlight && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-blue-500 text-black text-xs font-bold px-4 py-1 rounded-full">
                  MOST POPULAR
                </span>
              </div>
            )}

            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold mb-3">{plan.name}</h2>
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-5xl font-bold tracking-tight">{plan.price}</span>
                <span className="text-white/30 text-sm">{plan.period}</span>
              </div>
              <p className="text-white/30 text-sm mt-2">{plan.credits} assessments</p>
            </div>

            <ul className="space-y-3 mb-8">
              {plan.features.map((feature, i) => (
                <li key={i} className="flex items-center gap-3 text-sm text-white/60">
                  <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>

            <button
              onClick={() => !plan.disabled && handleCheckout(plan.id)}
              disabled={plan.disabled}
              className={`w-full py-3.5 rounded-full font-semibold text-sm transition-all ${
                plan.disabled
                  ? "bg-white/5 text-white/20 cursor-not-allowed"
                  : plan.highlight
                  ? "bg-white text-black hover:bg-white/90"
                  : "bg-white/5 text-white hover:bg-white/10 border border-white/10"
              }`}
            >
              {plan.cta}
            </button>
          </div>
        ))}
      </div>

      {/* Trust Badges */}
      <div className="glass-card">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center text-sm">
          <div>
            <div className="text-2xl mb-1">🔒</div>
            <div className="text-white/60">Secure Payments</div>
            <div className="text-white/25 text-xs">Stripe UK</div>
          </div>
          <div>
            <div className="text-2xl mb-1">🛡️</div>
            <div className="text-white/60">Zero Hallucination</div>
            <div className="text-white/25 text-xs">Citation validated</div>
          </div>
          <div>
            <div className="text-2xl mb-1">⚖️</div>
            <div className="text-white/60">FJR Triple-Gate</div>
            <div className="text-white/25 text-xs">Fair · Just · Reasonable</div>
          </div>
          <div>
            <div className="text-2xl mb-1">🇬🇧</div>
            <div className="text-white/60">UK Contract Law</div>
            <div className="text-white/25 text-xs">England & Wales</div>
          </div>
        </div>
      </div>
    </main>
  );
}
