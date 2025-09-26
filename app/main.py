from fastapi import FastAPI, File, UploadFile, Form
import shutil
import os
import subprocess
from app.transcription import transcribe_audio
from app.supabase_client import store_transcript
from datetime import datetime

app = FastAPI(title="BizExpress Backend", version="1.0.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio file to mono WAV 16kHz using ffmpeg.
    Returns path to converted WAV.
    """
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}_converted.wav"
    cmd = ["ffmpeg", "-y", "-i", input_path, "-ac", "1", "-ar", "16000", output_path]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg conversion failed: {e.stderr.decode()}")
    return output_path

@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...), user_email: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Convert to mono WAV 16kHz
        wav_path = convert_to_wav(file_path)

        # Transcribe audio
        transcript = transcribe_audio(wav_path)

        # Store transcript
        store_transcript(user_email, transcript)

        response = {"status": "success", "transcript": transcript}

    except Exception as e:
        response = {"status": "error", "message": str(e)}

    finally:
        # Cleanup uploaded and converted files
        if os.path.exists(file_path):
            os.remove(file_path)
        if 'wav_path' in locals() and os.path.exists(wav_path):
            os.remove(wav_path)

    return response

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
