"""
SAIF Supabase Client — ILRMF v3.0 Secure Client
"""
import os
from supabase import create_client, Client

def get_supabase() -> Client:
    """Initialize and return the Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError("Supabase URL and Key must be set in environment")

    return create_client(url, key)


# Singleton instance — reuse across the app
supabase = get_supabase()
