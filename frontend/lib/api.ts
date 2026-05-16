const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
async function apiFetch(path: string, opts: RequestInit = {}) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('saif_token') : null;
    const headers: any = { 'Content-Type': 'application/json', ...opts.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(`${API}${path}`, { ...opts, headers });
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || 'API Error');
    return res.json();
}
export const auth = {
    register: (email: string, password: string, full_name: string) => apiFetch('/api/v1/auth/register', { method: 'POST', body: JSON.stringify({ email, password, full_name }) }),
    login: (email: string, password: string) => apiFetch('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
};
export const assess = {
    analyze: (data: any) => apiFetch('/api/v1/assess/analyze', { method: 'POST', body: JSON.stringify(data) }),
    history: () => apiFetch('/api/v1/assess/history'),
};
export const payment = {
    checkout: (plan: string, success_url: string, cancel_url: string) => apiFetch('/api/v1/payment/checkout', { method: 'POST', body: JSON.stringify({ plan, success_url, cancel_url }) }),
    plans: () => apiFetch('/api/v1/payment/plans'),
};
