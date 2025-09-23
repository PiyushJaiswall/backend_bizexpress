import os
from supabase import create_client, Client

# Load environment variables (can also use Render's environment secrets)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
