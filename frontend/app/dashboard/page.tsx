'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { assess, payment } from '@/lib/api';
export default function Dashboard() {
    const [credits, setCredits] = useState(0); const [history, setHistory] = useState<any[]>([]);
    useEffect(() => {
        if (!localStorage.getItem('saif_token')) { window.location.href = '/auth/login'; return; }
        payment.plans().catch(()=>{}); // just to test auth
        assess.history().then(r => setHistory(r.data || [])).catch(()=>{});
    }, []);
    return (<div className="min-h-screen px-4 py-8 max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <Link href="/assess" className="saif-btn saif-btn-primary">New Assessment</Link>
        </div>
        <div className="saif-card mb-8 flex justify-between items-center"><h2 className="text-lg">Credits</h2><span className="text-3xl font-bold text-blue-400">{credits}</span></div>
        <h2 className="text-xl font-semibold mb-4">History</h2>
        {history.length === 0 ? <div className="saif-card text-gray-400 text-center">No assessments yet.</div> : 
            history.map((h: any) => <div key={h.id} className="saif-card mb-3 flex justify-between"><span>{h.contract_type}</span><span className="text-gray-400">{new Date(h.created_at).toLocaleDateString()}</span></div>)
        }
    </div>);
}
