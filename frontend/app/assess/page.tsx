'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { assess } from '@/lib/api';
export default function Assess() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [form, setForm] = useState({ claimant: '', defendant: '', contractType: 'Commercial', contractCategory: 'B2B', value: '', narrative: '', disputedClause: '', bargainingPower: 'equal', noticeAdequate: true, standardForm: false, consumerVulnerable: false, allowsUnilateralVariation: false, phase: 1 });

    useEffect(() => { if (!localStorage.getItem('saif_token')) router.push('/auth/login'); }, []);

    const handleSubmit = async (e: any) => {
        e.preventDefault(); setLoading(true);
        try {
            const result = await assess.analyze({ ...form, value: form.value ? parseFloat(form.value) : undefined });
            sessionStorage.setItem('saif_result', JSON.stringify(result));
            router.push('/result');
        } catch (e: any) { alert(e.message); } finally { setLoading(false); }
    };

    return (<div className="min-h-screen px-4 py-8 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">ILRMF Assessment</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
                <input value={form.claimant} onChange={e=>setForm({...form, claimant:e.target.value})} className="saif-input" placeholder="Claimant *" required />
                <input value={form.defendant} onChange={e=>setForm({...form, defendant:e.target.value})} className="saif-input" placeholder="Defendant *" required />
            </div>
            <div className="grid grid-cols-3 gap-4">
                <select value={form.contractCategory} onChange={e=>setForm({...form, contractCategory:e.target.value})} className="saif-input"><option value="B2B">B2B</option><option value="B2C">B2C</option></select>
                <input type="number" value={form.value} onChange={e=>setForm({...form, value:e.target.value})} className="saif-input" placeholder="Value (£)" />
                <select value={form.bargainingPower} onChange={e=>setForm({...form, bargainingPower:e.target.value})} className="saif-input"><option value="equal">Equal</option><option value="claimant_weaker">Claimant Weaker</option><option value="significant_imbalance">Imbalance</option></select>
            </div>
            <textarea value={form.narrative} onChange={e=>setForm({...form, narrative:e.target.value})} className="saif-input min-h-[120px]" placeholder="Narrative & Facts *" required />
            <textarea value={form.disputedClause} onChange={e=>setForm({...form, disputedClause:e.target.value})} className="saif-input min-h-[80px]" placeholder="Disputed Clause (optional)" />
            <button type="submit" disabled={loading} className="saif-btn saif-btn-primary w-full py-4 text-lg">{loading ? 'Analyzing...' : 'Run ILRMF Assessment'}</button>
        </form>
    </div>);
}
