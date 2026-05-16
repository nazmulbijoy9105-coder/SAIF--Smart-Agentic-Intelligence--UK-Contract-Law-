'use client';
import { useState } from 'react';
import Link from 'next/link';
import { auth } from '@/lib/api';
export default function Login() {
    const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState('');
    const handleSubmit = async (e: any) => {
        e.preventDefault(); setError('');
        try {
            const r = await auth.login(email, password);
            if (r.access_token) { localStorage.setItem('saif_token', r.access_token); window.location.href = '/dashboard'; }
        } catch (e: any) { setError(e.message); }
    };
    return (<div className="min-h-screen flex items-center justify-center px-4">
        <div className="saif-card w-full max-w-md">
            <h1 className="text-2xl font-bold mb-6">Sign In</h1>
            {error && <div className="bg-red-900/30 border border-red-700 p-3 rounded-lg mb-4 text-red-300 text-sm">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
                <input type="email" value={email} onChange={e=>setEmail(e.target.value)} className="saif-input" placeholder="Email" required />
                <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="saif-input" placeholder="Password" required />
                <button type="submit" className="saif-btn saif-btn-primary w-full py-3">Sign In</button>
            </form>
            <p className="mt-4 text-center text-sm text-gray-400">No account? <Link href="/auth/register" className="text-blue-400">Register</Link></p>
        </div>
    </div>);
}
