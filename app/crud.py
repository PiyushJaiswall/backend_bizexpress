from app.config import supabase
from datetime import datetime

def save_note(content: str, note_type: str, user_email: str):
    data = {
        "content": content,
        "type": note_type,
        "user_email": user_email,
        "timestamp": datetime.now().isoformat()
    }
    response = supabase.table("notes").insert(data).execute()
    return response.data

def fetch_user_notes(user_email: str):
    response = supabase.table("notes").select("*").eq("user_email", user_email).execute()
    return response.data
