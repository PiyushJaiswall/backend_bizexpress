from fastapi import FastAPI, File, UploadFile, Form
import shutil
import os
from app.transcription import transcribe_audio
from app.supabase_client import store_transcript

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...), user_email: str = Form(...)):
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
        os.remove(file_path)
