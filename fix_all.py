import os

# ==========================================
# FIX 1: Auth Router - Better error handling
# ==========================================
auth_code = '''"""
SAIF Auth Router - Fixed 401 errors
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, validator
import re
from app.db.supabase_client import supabase_db
from app.utils.logger import logger

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)

    @validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain a number")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(req: RegisterRequest, request: Request):
    try:
        result = await supabase_db.register(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
        )
        user = result.get("user")
        session = result.get("session")

        if not user:
            raise HTTPException(status_code=400, detail="Registration failed")

        access_token = None
        if session:
            access_token = session.access_token

        return {
            "success": True,
            "message": "Registration successful",
            "user_id": user.id,
            "access_token": access_token,
            "engine": "ILRMF v1.0",
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        logger.error(f"Registration error: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)


@router.post("/login")
async def login(req: LoginRequest, request: Request):
    try:
        result = await supabase_db.login(
            email=req.email,
            password=req.password,
        )
        session = result.get("session")
        user = result.get("user")

        if not session:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        profile = await supabase_db.get_profile(user.id)

        return {
            "success": True,
            "access_token": session.access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "full_name": profile.get("full_name", "") if profile else "",
            "credits_remaining": profile.get("credits_remaining", 0) if profile else 0,
            "plan": profile.get("plan", "free") if profile else "free",
            "engine": "ILRMF v1.0",
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid login" in error_msg.lower() or "invalid credentials" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if "email not confirmed" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Please confirm your email first. Check your inbox.")
        logger.error(f"Login error: {error_msg}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/me")
async def get_me(request: Request):
    from app.utils.auth import get_current_user
    user = await get_current_user(request)
    profile = await supabase_db.get_profile(user["id"])
    return {
        "success": True,
        "user": user,
        "profile": profile,
        "engine": "ILRMF v1.0",
    }
'''

with open('backend/app/routers/auth.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(auth_code)
print("OK: auth.py")


# ==========================================
# FIX 2: Supabase Client - Auto-create profile on login
# ==========================================
db_code = '''"""
SAIF Supabase Client - Auth + Data Layer
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.logger import logger
from typing import Optional, Dict, List


class SupabaseDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._admin = None
            cls._instance._initialized = False
        return cls._instance

    def _ensure_init(self):
        if self._initialized:
            return
        try:
            settings = get_settings()
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            if settings.SUPABASE_SERVICE_ROLE_KEY:
                self._admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            else:
                self._admin = self._client
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Supabase init failed: {e}")
            raise
        self._initialized = True

    @property
    def client(self):
        self._ensure_init()
        return self._client

    @property
    def admin_client(self):
        self._ensure_init()
        return self._admin

    async def register(self, email: str, password: str, full_name: str) -> Dict:
        try:
            result = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"full_name": full_name}}
            })
            if result.user:
                try:
                    self.admin_client.table("profiles").insert({
                        "id": result.user.id,
                        "email": email,
                        "full_name": full_name,
                        "credits_remaining": 3,
                        "plan": "free",
                        "created_by_engine": "ILRMF v1.0",
                    }).execute()
                except Exception as e:
                    logger.warning(f"Profile insert issue (may already exist): {e}")
                logger.info(f"User registered: {email}")
            return {"user": result.user, "session": result.session}
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            raise

    async def login(self, email: str, password: str) -> Dict:
        try:
            result = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            user = result.user
            # Auto-create profile if missing
            if user:
                profile = await self.get_profile(user.id)
                if not profile:
                    try:
                        self.admin_client.table("profiles").insert({
                            "id": user.id,
                            "email": email,
                            "full_name": user.user_metadata.get("full_name", email.split("@")[0]),
                            "credits_remaining": 3,
                            "plan": "free",
                        }).execute()
                        logger.info(f"Auto-created profile for: {email}")
                    except Exception:
                        pass
            return {"user": result.user, "session": result.session}
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

    async def verify_token(self, token: str) -> Optional[Dict]:
        try:
            result = self.client.auth.get_user(token)
            return result.user
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    async def get_profile(self, user_id: str) -> Optional[Dict]:
        try:
            result = self.admin_client.table("profiles").select("*").eq("id", user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Profile fetch failed: {e}")
            return None

    async def decrement_credit(self, user_id: str) -> bool:
        try:
            profile = await self.get_profile(user_id)
            if not profile or profile.get("credits_remaining", 0) <= 0:
                return False
            self.admin_client.table("profiles").update({
                "credits_remaining": profile["credits_remaining"] - 1,
            }).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Credit decrement failed: {e}")
            return False

    async def set_credits(self, user_id: str, amount: int, plan: str = "pro") -> bool:
        try:
            self.admin_client.table("profiles").update({
                "credits_remaining": amount,
                "plan": plan,
            }).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Credit set failed: {e}")
            return False

    async def save_assessment(self, user_id: str, data: Dict) -> str:
        try:
            result = self.admin_client.table("assessments").insert({"user_id": user_id, **data}).execute()
            return result.data[0]["id"] if result.data else "saved"
        except Exception as e:
            logger.error(f"Assessment save failed: {e}")
            return "failed"

    async def get_assessment_history(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        try:
            result = self.admin_client.table("assessments").select("*").eq("user_id", user_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            logger.error(f"History fetch failed: {e}")
            return []

    async def health_check(self) -> bool:
        try:
            self.client.table("profiles").select("id").limit(1).execute()
            return True
        except Exception:
            return False


supabase_db = SupabaseDB()
'''

with open('backend/app/db/supabase_client.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(db_code)
print("OK: supabase_client.py")


# ==========================================
# FIX 3: Premium Frontend - globals.css
# ==========================================
css_code = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg-primary: #000000;
  --bg-secondary: #0a0a0a;
  --bg-surface: #111111;
  --bg-elevated: #1a1a1a;
  --border-subtle: rgba(255,255,255,0.06);
  --border-medium: rgba(255,255,255,0.1);
  --text-primary: #f5f5f7;
  --text-secondary: #86868b;
  --text-tertiary: #48484a;
  --accent-blue: #2997ff;
  --accent-purple: #bf5af2;
  --accent-green: #30d158;
  --accent-orange: #ff9f0a;
  --accent-red: #ff453a;
  --glass-bg: rgba(255,255,255,0.03);
  --glass-border: rgba(255,255,255,0.06);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; }

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.5;
  letter-spacing: -0.01em;
}

/* ── Glass Card ─────────────────────────────── */
.glass-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  padding: 32px;
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.glass-card:hover {
  border-color: rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
}

/* ── Premium Input ──────────────────────────── */
.premium-input {
  width: 100%;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 14px 16px;
  color: var(--text-primary);
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s ease;
}

.premium-input::placeholder {
  color: var(--text-tertiary);
}

.premium-input:focus {
  border-color: var(--accent-blue);
  background: rgba(41,151,255,0.04);
  box-shadow: 0 0 0 3px rgba(41,151,255,0.12);
}

/* ── Premium Buttons ────────────────────────── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 28px;
  background: var(--text-primary);
  color: var(--bg-primary);
  border: none;
  border-radius: 980px;
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: -0.01em;
}

.btn-primary:hover {
  transform: scale(1.02);
  opacity: 0.9;
}

.btn-primary:active {
  transform: scale(0.98);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 28px;
  background: transparent;
  color: var(--accent-blue);
  border: none;
  border-radius: 980px;
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(41,151,255,0.08);
}

/* ── Gradient Text ──────────────────────────── */
.gradient-text {
  background: linear-gradient(135deg, #2997ff 0%, #bf5af2 50%, #ff6b6b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-blue {
  background: linear-gradient(135deg, #2997ff, #5ac8fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ── FJR Gate Cards ─────────────────────────── */
.gate-pass {
  background: rgba(48,209,88,0.08);
  border: 1px solid rgba(48,209,88,0.2);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}

.gate-fail {
  background: rgba(255,69,58,0.08);
  border: 1px solid rgba(255,69,58,0.2);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}

/* ── Animations ─────────────────────────────── */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.animate-in {
  animation: fadeIn 0.5s ease forwards;
}

.animate-pulse {
  animation: pulse 2s ease-in-out infinite;
}

/* ── Scrollbar ──────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Selection ──────────────────────────────── */
::selection {
  background: rgba(41,151,255,0.3);
  color: white;
}
'''

with open('frontend/app/globals.css', 'w', encoding='utf-8', newline='\n') as f:
    f.write(css_code)
print("OK: globals.css")


# ==========================================
# FIX 4: Premium Layout
# ==========================================
layout_code = '''import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SAIF — UK Contract Law AI",
  description: "Smart Agentic Intelligence Framework — ILRMF Engine",
  keywords: ["UK contract law", "AI legal analysis", "ILRMF", "SAIF"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-black antialiased">
        {children}
      </body>
    </html>
  );
}
'''

with open('frontend/app/layout.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(layout_code)
print("OK: layout.tsx")


# ==========================================
# FIX 5: Premium Landing Page
# ==========================================
landing_code = '''import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-purple-500/8 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 text-center max-w-3xl animate-in">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 mb-8">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs font-medium text-white/60 tracking-wide">
            ILRMF Engine v1.0 — NB TECH Bangladesh
          </span>
        </div>

        {/* Title */}
        <h1 className="text-7xl md:text-8xl font-bold tracking-tight mb-6 gradient-text">
          SAIF
        </h1>

        <p className="text-xl md:text-2xl text-white/70 font-light mb-2 tracking-tight">
          Smart Agentic Intelligence Framework
        </p>

        <p className="text-lg text-white/40 font-light mb-12">
          UK Contract Law AI — Fair · Just · Reasonable
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Link href="/assess" className="btn-primary text-lg px-10 py-4">
            Start Assessment
          </Link>
          <Link href="/pricing" className="btn-secondary text-lg px-10 py-4">
            View Plans
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 max-w-md mx-auto">
          <div>
            <div className="text-3xl font-bold gradient-text-blue">ZERO</div>
            <div className="text-xs text-white/40 mt-1 uppercase tracking-wider">Hallucination</div>
          </div>
          <div>
            <div className="text-3xl font-bold gradient-text-blue">FJR</div>
            <div className="text-xs text-white/40 mt-1 uppercase tracking-wider">Triple-Gate</div>
          </div>
          <div>
            <div className="text-3xl font-bold gradient-text-blue">4</div>
            <div className="text-xs text-white/40 mt-1 uppercase tracking-wider">Court Tracks</div>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-16 text-xs text-white/20">
          Created by Md Nazmul Islam (Bijoy) — Advocate, Supreme Court of Bangladesh
        </p>
      </div>
    </main>
  );
}
'''

with open('frontend/app/page.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(landing_code)
print("OK: page.tsx")


# ==========================================
# FIX 6: Premium Login Page
# ==========================================
login_code = '''"use client";
import { useState } from "react";
import Link from "next/link";
import { auth } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await auth.login(email, password);
      if (result.access_token) {
        localStorage.setItem("saif_token", result.access_token);
        localStorage.setItem("saif_user", JSON.stringify({
          id: result.user_id,
          email: result.email,
          full_name: result.full_name || "",
          credits: result.credits_remaining || 0,
          plan: result.plan || "free",
        }));
        window.location.href = "/dashboard";
      }
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-6 relative">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-blue-500/8 rounded-full blur-[100px] pointer-events-none" />

      <div className="glass-card w-full max-w-md relative z-10 animate-in">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Sign In</h1>
          <p className="text-white/40 text-sm">SAIF — UK Contract Law AI</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-12 p-4 mb-6 text-red-300 text-sm rounded-xl">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="premium-input"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="premium-input"
              placeholder="Enter your password"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full mt-2"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-white/30">
          Don&apos;t have an account?{" "}
          <Link href="/auth/register" className="text-blue-400 hover:text-blue-300 transition-colors">
            Create one
          </Link>
        </p>
      </div>
    </main>
  );
}
'''

with open('frontend/app/auth/login/page.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(login_code)
print("OK: login/page.tsx")


# ==========================================
# FIX 7: Premium Register Page
# ==========================================
register_code = '''"use client";
import { useState } from "react";
import Link from "next/link";
import { auth } from "@/lib/api";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await auth.register(email, password, fullName);
      if (result.access_token) {
        localStorage.setItem("saif_token", result.access_token);
        localStorage.setItem("saif_user", JSON.stringify({
          id: result.user_id,
          email: email,
          full_name: fullName,
          credits: 3,
          plan: "free",
        }));
        window.location.href = "/dashboard";
      } else {
        setSuccess(true);
      }
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <main className="min-h-screen flex items-center justify-center px-6">
        <div className="glass-card max-w-md text-center animate-in">
          <div className="w-16 h-16 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-2">Check Your Email</h1>
          <p className="text-white/40 mb-8">We sent a confirmation link to {email}</p>
          <Link href="/auth/login" className="btn-primary">
            Go to Sign In
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6 relative">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-purple-500/8 rounded-full blur-[100px] pointer-events-none" />

      <div className="glass-card w-full max-w-md relative z-10 animate-in">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Create Account</h1>
          <p className="text-white/40 text-sm">3 free assessments included</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-red-300 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Full Name</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="premium-input"
              placeholder="Your full name"
              required
              minLength={2}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="premium-input"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="premium-input"
              placeholder="8+ chars, uppercase, number"
              required
              minLength={8}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full mt-2"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-white/30">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-blue-400 hover:text-blue-300 transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
'''

with open('frontend/app/auth/register/page.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(register_code)
print("OK: register/page.tsx")


# ==========================================
# FIX 8: Premium Dashboard
# ==========================================
dashboard_code = '''"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { assess, payment } from "@/lib/api";

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [credits, setCredits] = useState(0);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("saif_user");
    if (!stored) {
      window.location.href = "/auth/login";
      return;
    }
    setUser(JSON.parse(stored));
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [creditsData, historyData] = await Promise.all([
        payment.credits().catch(() => ({ credits_remaining: 0 })),
        assess.history().catch(() => ({ data: [] })),
      ]);
      setCredits(creditsData.credits_remaining || 0);
      setHistory(historyData.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("saif_token");
    localStorage.removeItem("saif_user");
    window.location.href = "/";
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-white/40">Loading...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-white/40 mt-1">{user?.email} — ILRMF v1.0</p>
        </div>
        <div className="flex gap-3">
          <Link href="/assess" className="btn-primary px-6">
            New Assessment
          </Link>
          <button onClick={handleLogout} className="btn-secondary px-6">
            Sign Out
          </button>
        </div>
      </div>

      {/* Credits Card */}
      <div className="glass-card mb-8 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-white/40 uppercase tracking-wider mb-1">Credits Remaining</p>
          <p className="text-sm text-white/50">Each assessment uses 1 credit</p>
        </div>
        <div className="text-5xl font-bold gradient-text-blue">{credits}</div>
        {credits <= 1 && (
          <Link href="/pricing" className="btn-primary text-sm px-5 py-2.5">
            Get Credits
          </Link>
        )}
      </div>

      {/* History */}
      <h2 className="text-xl font-semibold mb-4 tracking-tight">Assessment History</h2>
      {history.length === 0 ? (
        <div className="glass-card text-center py-12">
          <p className="text-white/30 mb-4">No assessments yet</p>
          <Link href="/assess" className="btn-primary">
            Start your first assessment
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item: any) => (
            <div key={item.id} className="glass-card flex items-center justify-between py-4">
              <div>
                <p className="font-medium">{item.contract_type || "Assessment"}</p>
                <p className="text-sm text-white/30">
                  {new Date(item.created_at).toLocaleDateString("en-GB", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                  {" · "}
                  {item.court_track || "N/A"}
                </p>
              </div>
              <span className={`text-sm font-mono ${
                (item.overall_risk_score || 0) >= 60
                  ? "text-green-400"
                  : "text-orange-400"
              }`}>
                {item.overall_risk_score || "—"}
              </span>
            </div>
          ))}
        </div>
      )}

      <p className="mt-12 text-center text-xs text-white/15">
        ILRMF Engine v1.0 — Md Nazmul Islam (Bijoy) — NB TECH Bangladesh
      </p>
    </main>
  );
}
'''

with open('frontend/app/dashboard/page.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(dashboard_code)
print("OK: dashboard/page.tsx")


# ==========================================
# FIX 9: Premium Assess Page
# ==========================================
assess_code = '''"use client";
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
'''

with open('frontend/app/assess/page.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(assess_code)
print("OK: assess/page.tsx")


# ==========================================
# FIX 10: Premium Result Page
# ==========================================
result_code = '''"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { exportToPDF } from "@/lib/pdf-export";

export default function ResultPage() {
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("saif_result");
    if (!stored) {
      window.location.href = "/assess";
      return;
    }
    setResult(JSON.parse(stored));
  }, []);

  if (!result) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-white/40">Loading...</div>
      </main>
    );
  }

  const data = result.data || {};
  const facts = data.facts || {};
  const issues = data.issues || [];
  const relief = data.relief || {};
  const governance = data.governance || {};

  return (
    <main className="min-h-screen px-6 py-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-10">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">ILRMF Result</h1>
          <p className="text-white/30 text-sm mt-1">
            ID: {result.assessment_id} · Phase {result.phase}
          </p>
        </div>
        <button
          onClick={() => exportToPDF({ ...data, assessment_id: result.assessment_id })}
          className="btn-secondary text-sm"
        >
          Export Report
        </button>
      </div>

      {/* Governance Banner */}
      <div className={`glass-card mb-6 border-l-4 ${
        governance.hallucination === "ZERO" ? "border-l-green-400" : "border-l-red-400"
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-medium text-white/40 uppercase tracking-wider">Hallucination Status</span>
            <p className={`text-lg font-bold mt-1 ${
              governance.hallucination === "ZERO" ? "text-green-400" : "text-red-400"
            }`}>
              {governance.hallucination === "ZERO" ? "✓ ZERO" : "✗ FLAGGED"}
            </p>
          </div>
          <div className="text-right text-xs text-white/30">
            {governance.citationValidation && (
              <>
                <div>Verified: {governance.citationValidation.verified_count || 0}</div>
                <div>Flagged: {governance.citationValidation.flagged_count || 0}</div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Facts */}
      <div className="glass-card mb-6">
        <h2 className="text-lg font-semibold mb-4 tracking-tight">Facts</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div><span className="text-white/40">Parties:</span> <span className="text-white/80">{facts.parties || "N/A"}</span></div>
          <div><span className="text-white/40">Type:</span> <span className="text-white/80">{facts.contractType || "N/A"}</span></div>
          <div><span className="text-white/40">Category:</span> <span className="text-white/80">{facts.consumerType || "N/A"}</span></div>
          <div><span className="text-white/40">Value:</span> <span className="text-white/80">{facts.value || "N/A"}</span></div>
          <div><span className="text-white/40">Bargaining:</span> <span className="text-white/80">{facts.bargainingPower || "N/A"}</span></div>
          <div><span className="text-white/40">Standard Form:</span> <span className="text-white/80">{facts.standardForm ? "Yes" : "No"}</span></div>
        </div>
        {facts.disputedClause && (
          <div className="mt-4 p-4 bg-orange-500/5 border border-orange-500/10 rounded-xl text-sm">
            <span className="text-orange-300 font-medium">Disputed Clause:</span>{" "}
            <span className="text-white/60">{facts.disputedClause}</span>
          </div>
        )}
      </div>

      {/* Issues & FJR */}
      <h2 className="text-lg font-semibold mb-4 tracking-tight">
        Issues & FJR Triple-Gate ({issues.length})
      </h2>

      {issues.length === 0 ? (
        <div className="glass-card text-center py-8 text-white/30">
          No issues identified — the contract appears compliant.
        </div>
      ) : (
        issues.map((issue: any, idx: number) => {
          const fjr = issue.fjr || {};
          const score = fjr.score || 0;
          const scoreColor = score >= 70 ? "text-green-400" : score >= 40 ? "text-orange-400" : "text-red-400";

          return (
            <div key={idx} className="glass-card mb-4">
              {/* Issue Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg tracking-tight">Issue {idx + 1}</h3>
                  <p className="text-white/50 text-sm mt-1">{issue.issue}</p>
                </div>
                <div className="text-4xl font-bold font-mono ml-4">
                  <span className={scoreColor}>{score}</span>
                  <span className="text-white/20 text-lg">/100</span>
                </div>
              </div>

              {/* Law */}
              <div className="p-4 bg-white/[0.02] rounded-xl text-sm mb-4 border border-white/[0.04]">
                <span className="text-white/40 font-medium">Law: </span>
                <span className="text-white/70">{issue.law || "Not specified"}</span>
              </div>

              {/* FJR Gates */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className={fjr.fair ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-white/40 uppercase tracking-wider">Fair</div>
                  <div className={`text-xl font-bold ${fjr.fair ? "text-green-400" : "text-red-400"}`}>
                    {fjr.fair ? "✓" : "✗"}
                  </div>
                  {fjr.fairScore !== undefined && (
                    <div className="text-[10px] text-white/30">{fjr.fairScore}/100</div>
                  )}
                </div>
                <div className={fjr.just ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-white/40 uppercase tracking-wider">Just</div>
                  <div className={`text-xl font-bold ${fjr.just ? "text-green-400" : "text-red-400"}`}>
                    {fjr.just ? "✓" : "✗"}
                  </div>
                  {fjr.justScore !== undefined && (
                    <div className="text-[10px] text-white/30">{fjr.justScore}/100</div>
                  )}
                </div>
                <div className={fjr.reasonable ? "gate-pass" : "gate-fail"}>
                  <div className="text-[10px] font-medium text-white/40 uppercase tracking-wider">Reasonable</div>
                  <div className={`text-xl font-bold ${fjr.reasonable ? "text-green-400" : "text-red-400"}`}>
                    {fjr.reasonable ? "✓" : "✗"}
                  </div>
                  {fjr.reasonableScore !== undefined && (
                    <div className="text-[10px] text-white/30">{fjr.reasonableScore}/100</div>
                  )}
                </div>
              </div>

              {/* Arguments */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded-xl">
                  <div className="text-blue-400 text-xs font-semibold mb-1 uppercase tracking-wider">Claimant</div>
                  <p className="text-sm text-white/60">{issue.argument?.claimant || "N/A"}</p>
                </div>
                <div className="p-4 bg-purple-500/5 border border-purple-500/10 rounded-xl">
                  <div className="text-purple-400 text-xs font-semibold mb-1 uppercase tracking-wider">Defendant</div>
                  <p className="text-sm text-white/60">{issue.argument?.defendant || "N/A"}</p>
                </div>
              </div>

              {/* Verdict */}
              <div className={`p-4 rounded-xl text-sm font-medium ${
                issue.verdict?.includes("ENFORCEABLE")
                  ? "bg-green-500/8 text-green-300 border border-green-500/15"
                  : issue.verdict?.includes("VOID") && !issue.verdict?.includes("LIKELY")
                  ? "bg-red-500/8 text-red-300 border border-red-500/15"
                  : "bg-orange-500/8 text-orange-300 border border-orange-500/15"
              }`}>
                {issue.verdict || "Not assessed"}
              </div>
            </div>
          );
        })
      )}

      {/* Relief */}
      <div className="glass-card mb-6">
        <h2 className="text-lg font-semibold mb-4 tracking-tight">Relief & Remedies</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-white/40">Primary:</span>{" "}
            <span className="text-white/80">{relief.primary || "N/A"}</span>
          </div>
          <div>
            <span className="text-white/40">Damages:</span>{" "}
            <span className="text-white/80">{relief.damages || "N/A"}</span>
          </div>
          <div>
            <span className="text-white/40">Court:</span>{" "}
            <span className="text-white/80">{relief.court || "N/A"}</span>
          </div>
          <div>
            <span className="text-white/40">Probability:</span>{" "}
            <span className="text-white/80">{relief.probability || 0}%</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-4 mb-8">
        <Link href="/assess" className="btn-primary">
          New Assessment
        </Link>
        <Link href="/dashboard" className="btn-secondary">
          Dashboard
        </Link>
      </div>

      <p className="text-center text-xs text-white/15">
        ILRMF Engine v1.0 — AI-assisted analysis. Not legal advice. Consult a qualified solicitor.
      </p>
    </main>
  );
}
'''

with open('frontend/app/result/page.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(result_code)
print("OK: result/page.tsx")


# ==========================================
# FIX 11: Premium Pricing Page
# ==========================================
pricing_code = '''"use client";
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
'''

with open('frontend/app/pricing/page.tsx', 'w', encoding='utf-8', newline='\n') as f:
    f.write(pricing_code)
print("OK: pricing/page.tsx")


# ==========================================
# FIX 12: API client - better error handling
# ==========================================
api_code = """const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
"""

with open('frontend/lib/api.ts', 'w', encoding='utf-8', newline='\n') as f:
    f.write(api_code)
print("OK: api.ts")


print("\n=== ALL FILES WRITTEN SUCCESSFULLY ===")
