from supabase import create_client
from api.config.settings import settings

supabase = create_client(
    settings.NEXT_PUBLIC_SUPABASE_URL,
    settings.NEXT_PUBLIC_SUPABASE_ANON_KEY,
)
