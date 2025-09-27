from app.supabase_client import supabase
from transformers import pipeline
from datetime import datetime
import re

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="t5-small")

def generate_meeting_from_transcript(transcript_id: str, transcript_text: str):
    """
    Generate AI summary, key points, followup points, title from transcript
    and insert into meetings table
    """
    # 1. Generate summary
    summary_result = summarizer(transcript_text, max_length=150, min_length=50, do_sample=False)
    summary_text = summary_result[0]['summary_text']

    # 2. Title - first sentence or generated
    title = transcript_text.split(".")[0] if transcript_text else "Meeting"

    # 3. Key points - simple heuristic: top 5 sentences longer than 20 chars
    key_points = [s.strip() for s in transcript_text.split(".") if len(s) > 20][:5]

    # 4. Followup points - heuristic or placeholder
    followup_points = ["Follow up point 1", "Follow up point 2"]

    # 5. Next meeting schedule - detect date-like strings
    date_matches = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", transcript_text)
    next_meet_schedule = date_matches[0] if date_matches else None

    # 6. Insert into meetings table
    supabase.table("meetings").insert({
        "transcript_id": transcript_id,
        "title": title,
        "summary": summary_text,
        "key_points": key_points,
        "followup_points": followup_points,
        "next_meet_schedule": next_meet_schedule,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }).execute()
