import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_transcript(client_id: str, meeting_title: str, audio_url: str, transcript_text: str):
    """
    Store a transcript in the 'transcripts' table
    """
    response = supabase.table("transcripts").insert({
        "client_id": client_id,
        "meeting_title": meeting_title,
        "audio_url": audio_url,
        "transcript_text": transcript_text
    }).execute()

    if response.error:
        raise Exception(f"Failed to store transcript: {response.error}")
    
    return response.data
