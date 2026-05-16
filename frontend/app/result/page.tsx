'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { exportToPDF } from '@/lib/pdf-export';
export default function Result() {
    const [result, setResult] = useState<any>(null);
    useEffect(() => { const s = sessionStorage.getItem('saif_result'); if (s) setResult(JSON.parse(s)); else window.location.href = '/assess'; }, []);
    if (!result) return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>;
    const data = result.data || {}; const issues = data.issues || []; const relief = data.relief || {}; const gov = data.governance || {};
    return (<div className="min-h-screen px-4 py-8 max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
            <div><h1 className="text-3xl font-bold">ILRMF Result</h1><p className="text-gray-400 text-sm">ID: {result.assessment_id}</p></div>
            <button onClick={() => exportToPDF(data)} className="saif-btn saif-btn-secondary">📄 Export</button>
        </div>
        <div className={`saif-card mb-6 border-l-4 ${gov.hallucination==='ZERO'?'border-l-green-500':'border-l-red-500'}`}>
            <span className="font-semibold">Hallucination: </span><span className={gov.hallucination==='ZERO'?'text-green-400':'text-red-400'}>{gov.hallucination}</span>
        </div>
        {issues.map((issue: any, idx: number) => (
            <div key={idx} className="saif-card mb-4">
                <div className="flex justify-between mb-3"><h3 className="font-semibold">Issue {idx+1}: {issue.issue}</h3><span className="text-2xl font-bold text-blue-400">{issue.fjr?.score||0}/100</span></div>
                <div className="grid grid-cols-3 gap-3 mb-3">
                    <div className={`p-3 rounded-lg text-center ${issue.fjr?.fair?'bg-green-900/30 border border-green-700':'bg-red-900/30 border border-red-700'}`}>FAIR: {issue.fjr?.fair?'✓':'✗'}</div>
                    <div className={`p-3 rounded-lg text-center ${issue.fjr?.just?'bg-green-900/30 border border-green-700':'bg-red-900/30 border border-red-700'}`}>JUST: {issue.fjr?.just?'✓':'✗'}</div>
                    <div className={`p-3 rounded-lg text-center ${issue.fjr?.reasonable?'bg-green-900/30 border border-green-700':'bg-red-900/30 border border-red-700'}`}>REASONABLE: {issue.fjr?.reasonable?'✓':'✗'}</div>
                </div>
                <div className={`p-3 rounded-lg text-sm ${issue.verdict?.includes('ENFORCEABLE')?'bg-green-900/30 text-green-300':'bg-red-900/30 text-red-300'}`}>{issue.verdict}</div>
            </div>
        ))}
        <div className="saif-card mb-6">
            <h2 className="text-xl font-semibold mb-3">Relief</h2>
            <div className="grid grid-cols-2 gap-3 text-sm"><div>Primary: {relief.primary}</div><div>Court: {relief.court}</div><div>Damages: {relief.damages}</div><div>Probability: {relief.probability}%</div></div>
        </div>
        <Link href="/assess" className="saif-btn saif-btn-primary">New Assessment</Link>
    </div>);
}
