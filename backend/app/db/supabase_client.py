"""
SAIF Supabase Client — Auth + Data Layer
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
            self._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY,
            )
            if settings.SUPABASE_SERVICE_ROLE_KEY:
                self._admin = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY,
                )
            else:
                self._admin = self._client
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Supabase init failed: {e}")
            raise
        self._initialized = True

    @property
    def client(self) -> Client:
        self._ensure_init()
        return self._client

    @property
    def admin_client(self) -> Client:
        self._ensure_init()
        return self._admin

    # ── Auth ──────────────────────────────────────────────
    async def register(self, email: str, password: str, full_name: str) -> Dict:
        try:
            result = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"full_name": full_name}}
            })
            if result.user:
                self.admin_client.table("profiles").insert({
                    "id": result.user.id,
                    "email": email,
                    "full_name": full_name,
                    "credits_remaining": 3,
                    "plan": "free",
                    "created_by_engine": "ILRMF v1.0",
                }).execute()
                logger.info(f"✅ User registered: {email}")
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

    # ── Profile / Credits ─────────────────────────────────
    async def get_profile(self, user_id: str) -> Optional[Dict]:
        try:
            result = (
                self.admin_client.table("profiles")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
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

    # ── Assessments ───────────────────────────────────────
    async def save_assessment(self, user_id: str, data: Dict) -> str:
        try:
            result = self.admin_client.table("assessments").insert({
                "user_id": user_id,
                **data,
            }).execute()
            return result.data[0]["id"] if result.data else "saved"
        except Exception as e:
            logger.error(f"Assessment save failed: {e}")
            return "failed"

    async def get_assessment_history(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict]:
        try:
            result = (
                self.admin_client.table("assessments")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"History fetch failed: {e}")
            return []

    # ── Health Check ──────────────────────────────────────
    async def health_check(self) -> bool:
        try:
            self.client.table("profiles").select("id").limit(1).execute()
            return True
        except Exception:
            return False


supabase_db = SupabaseDB()
