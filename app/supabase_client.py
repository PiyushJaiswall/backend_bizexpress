import os
from supabase import create_client

# Read credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_transcript(client_id: str, meeting_title: str, audio_url: str, transcript_text: str):
    """
    Store a transcript in the 'transcripts' table using Supabase Python v2
    """
    response = supabase.table("transcripts").insert({
        "client_id": client_id,
        "meeting_title": meeting_title,
        "audio_url": audio_url,
        "transcript_text": transcript_text
    }).execute()
    
    # Check for errors properly in Supabase v2
    if response.status_code >= 400:
        raise Exception(f"Failed to store transcript: {response.data}")
    
    return response.data
