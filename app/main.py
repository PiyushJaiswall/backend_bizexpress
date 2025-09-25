from fastapi import FastAPI, File, UploadFile, Form
import shutil
import os
from app.transcription import transcribe_audio
from app.supabase_client import store_transcript
from pydub import AudioSegment

app = FastAPI(title="BizExpress Backend", version="1.0.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def convert_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio.export(output_path, format="wav")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...), user_email: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    wav_path = file_path + ".wav"
    try:
        convert_to_wav(file_path, wav_path)
        transcript = transcribe_audio(wav_path)
        store_transcript(user_email, transcript)
        response = {"status": "success", "transcript": transcript}
    except Exception as e:
        response = {"status": "error", "message": str(e)}
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(wav_path):
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

