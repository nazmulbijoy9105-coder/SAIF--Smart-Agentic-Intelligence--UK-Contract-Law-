'use client';
import { useState } from 'react';
import Link from 'next/link';
import { auth } from '@/lib/api';
export default function Register() {
    const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [name, setName] = useState('');
    const [error, setError] = useState(''); const [success, setSuccess] = useState(false);
    const handleSubmit = async (e: any) => {
        e.preventDefault(); setError('');
        try { await auth.register(email, password, name); setSuccess(true); } catch (e: any) { setError(e.message); }
    };
    if (success) return (<div className="min-h-screen flex items-center justify-center px-4"><div className="saif-card text-center"><h1 className="text-2xl font-bold mb-4">Check Email</h1><Link href="/auth/login" className="saif-btn saif-btn-primary">Login</Link></div></div>);
    return (<div className="min-h-screen flex items-center justify-center px-4">
        <div className="saif-card w-full max-w-md">
            <h1 className="text-2xl font-bold mb-6">Create Account</h1>
            {error && <div className="bg-red-900/30 border border-red-700 p-3 rounded-lg mb-4 text-red-300 text-sm">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
                <input value={name} onChange={e=>setName(e.target.value)} className="saif-input" placeholder="Full Name" required />
                <input type="email" value={email} onChange={e=>setEmail(e.target.value)} className="saif-input" placeholder="Email" required />
                <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="saif-input" placeholder="Password" required />
                <button type="submit" className="saif-btn saif-btn-primary w-full py-3">Register</button>
            </form>
        </div>
    </div>);
}
