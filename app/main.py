from fastapi import FastAPI, File, UploadFile, Form
import shutil
import os
from app.transcription import transcribe_audio
from app.supabase_client import store_transcript

app = FastAPI(title="BizExpress Backend", version="1.0.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Backend is running"}


@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...), user_email: str = Form(...)):
    """
    Upload an audio file, transcribe it, and store in Supabase.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        transcript = transcribe_audio(file_path)
        store_transcript(user_email, transcript)
        return {"status": "success", "transcript": transcript}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/reminders/{user_email}")
async def get_reminders(user_email: str):
    now = datetime.utcnow().isoformat()
    response = supabase.table("meeting_schedules") \
        .select("*") \
        .eq("user_email", user_email) \
        .gte("scheduled_time", now) \
        .order("scheduled_time", desc=False) \
        .execute()

    return response.data
