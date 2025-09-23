from supabase import create_client, Client
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def store_transcript(
    user_email: str,
    transcript: str,
    meeting_name: str = None,
    start_time: str = None,
    end_time: str = None,
    duration: str = None,
    file_name: str = None
):
    """
    Stores meeting transcription and metadata into Supabase.
    """
    data = {
        "user_email": user_email,
        "transcript": transcript,
        "meeting_name": meeting_name,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "file_name": file_name
    }

    response = supabase.table("meeting_transcripts").insert(data).execute()
    
    if response.error:
        print("Error storing transcript:", response.error)
        return None
    return response.data
