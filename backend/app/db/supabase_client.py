from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.logger import logger
from typing import Optional, Dict, List

class SupabaseDB:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            s = get_settings()
            cls._instance._client = create_client(s.SUPABASE_URL, s.SUPABASE_KEY)
            cls._instance._admin = create_client(s.SUPABASE_URL, s.SUPABASE_SERVICE_ROLE_KEY) if s.SUPABASE_SERVICE_ROLE_KEY else cls._instance._client
        return cls._instance

    @property
    def client(self): return self._client
    @property
    def admin_client(self): return self._admin

    async def register(self, email: str, password: str, full_name: str) -> Dict:
        result = self.client.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": full_name}}})
        if result.user:
            self.admin_client.table("profiles").insert({"id": result.user.id, "email": email, "full_name": full_name, "created_by_engine": "ILRMF v1.0"}).execute()
        return {"user": result.user, "session": result.session}

    async def login(self, email: str, password: str) -> Dict:
        result = self.client.auth.sign_in_with_password({"email": email, "password": password})
        return {"user": result.user, "session": result.session}

    async def verify_token(self, token: str) -> Optional[Dict]:
        try: return self.client.auth.get_user(token).user
        except: return None

    async def get_profile(self, user_id: str) -> Optional[Dict]:
        try: return self.admin_client.table("profiles").select("*").eq("id", user_id).single().execute().data
        except: return None

    async def decrement_credit(self, user_id: str) -> bool:
        p = await self.get_profile(user_id)
        if not p or p.get("credits_remaining", 0) <= 0: return False
        self.admin_client.table("profiles").update({"credits_remaining": p["credits_remaining"] - 1}).eq("id", user_id).execute()
        return True

    async def set_credits(self, user_id: str, amount: int, plan: str = "pro") -> bool:
        try: self.admin_client.table("profiles").update({"credits_remaining": amount, "plan": plan}).eq("id", user_id).execute(); return True
        except: return False

    async def save_assessment(self, user_id: str, data: Dict) -> str:
        try:
            res = self.admin_client.table("assessments").insert({"user_id": user_id, **data}).execute()
            return res.data[0]["id"] if res.data else "saved"
        except: return "failed"

    async def get_assessment_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        try: return self.admin_client.table("assessments").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute().data
        except: return []

supabase_db = SupabaseDB()
