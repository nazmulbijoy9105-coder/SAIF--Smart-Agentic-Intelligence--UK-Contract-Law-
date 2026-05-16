'use client';
import { payment } from '@/lib/api';
export default function Pricing() {
    const handleCheckout = async (plan: string) => {
        if (!localStorage.getItem('saif_token')) { window.location.href = '/auth/login'; return; }
        try { const r = await payment.checkout(plan, `${window.location.origin}/dashboard`, `${window.location.origin}/pricing`); if (r.url) window.location.href = r.url; } catch (e: any) { alert(e.message); }
    };
    const plans = [
        { id: 'free', name: 'Free', price: '£0', credits: 3, cta: 'Current', disabled: true },
        { id: 'pro', name: 'Pro', price: '£19.99', credits: 50, cta: 'Upgrade', disabled: false },
        { id: 'enterprise', name: 'Enterprise', price: '£99.99', credits: 999, cta: 'Contact', disabled: false },
    ];
    return (<div className="min-h-screen px-4 py-12 max-w-5xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-8">Choose Your Plan</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map(p => (
                <div key={p.id} className={`saif-card ${p.id==='pro'?'border-blue-500 border-2':''}`}>
                    <h2 className="text-xl font-bold mb-2">{p.name}</h2>
                    <div className="text-4xl font-bold mb-4">{p.price}</div>
                    <p className="text-gray-400 mb-6">{p.credits} assessments</p>
                    <button onClick={() => handleCheckout(p.id)} disabled={p.disabled} className={`saif-btn w-full py-3 ${p.disabled?'saif-btn-secondary opacity-50':'saif-btn-primary'}`}>{p.cta}</button>
                </div>
            ))}
        </div>
    </div>);
}
