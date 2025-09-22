from fastapi import FastAPI, UploadFile, File
from app.models import NoteCreate
from app.crud import save_note, fetch_user_notes
from app.transcription import transcribe_audio
from app.summarization import generate_summary
from typing import List

app = FastAPI(title="Live Meeting Backend API")

@app.post("/notes/")
def create_note(note: NoteCreate):
    result = save_note(note.content, note.type, note.user_email)
    return {"status": "success", "data": result}

@app.get("/notes/{user_email}")
def get_notes(user_email: str):
    notes = fetch_user_notes(user_email)
    return {"status": "success", "notes": notes}

@app.post("/transcribe/")
async def upload_audio(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Transcribe and summarize
    text = transcribe_audio(file_location)
    summary = generate_summary(text)
    
    return {"transcription": text, "summary": summary}
