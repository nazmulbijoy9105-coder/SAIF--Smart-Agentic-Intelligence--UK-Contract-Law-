const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch(path: string, opts: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('saif_token') : null;
  const headers: any = { 'Content-Type': 'application/json', ...opts.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`${API}${path}`, { ...opts, headers });

    if (res.status === 401) {
      localStorage.removeItem('saif_token');
      localStorage.removeItem('saif_user');
      window.location.href = '/auth/login';
      throw new Error('Session expired. Please sign in again.');
    }

    if (res.status === 402) {
      throw new Error('No credits remaining. Please upgrade your plan.');
    }

    if (res.status === 429) {
      throw new Error('Rate limit exceeded. Please wait a moment.');
    }

    if (!res.ok) {
      const data = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(data.detail || `Error: ${res.status}`);
    }

    return res.json();
  } catch (err: any) {
    if (err.message && !err.message.includes('fetch')) throw err;
    throw new Error('Network error. Please check your connection.');
  }
}

export const auth = {
  register: (email: string, password: string, full_name: string) =>
    apiFetch('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    }),
  login: (email: string, password: string) =>
    apiFetch('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
};

export const assess = {
  analyze: (data: any) =>
    apiFetch('/api/v1/assess/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  history: (limit = 20, offset = 0) =>
    apiFetch(`/api/v1/assess/history?limit=${limit}&offset=${offset}`),
};

export const payment = {
  checkout: (plan: string, success_url: string, cancel_url: string) =>
    apiFetch('/api/v1/payment/checkout', {
      method: 'POST',
      body: JSON.stringify({ plan, success_url, cancel_url }),
    }),
  credits: () => apiFetch('/api/v1/payment/credits'),
  plans: () => apiFetch('/api/v1/payment/plans'),
};
