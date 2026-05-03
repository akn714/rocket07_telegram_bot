"""Supabase client for database operations."""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer service-role key for backend operations (bypasses restrictive RLS).
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

# Create client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def get_supabase() -> Client:
    """Get the Supabase client instance."""
    if not supabase:
        raise RuntimeError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY in .env")
    return supabase