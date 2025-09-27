from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
import uuid
import ffmpeg

from app.transcription import transcribe_audio
from app.supabase_client import store_transcript

app = FastAPI(title="BizExpress Backend", version="1.0.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def convert_to_wav(input_path: str, output_path: str):
    """
    Convert any audio file to WAV, mono, 16kHz PCM using ffmpeg-python
    """
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format='wav', ac=1, ar=16000)
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        raise Exception(f"Failed to convert audio: {e.stderr.decode()}")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/transcribe/")
async def transcribe(
    file: UploadFile = File(...),
    client_id: str = Form(...),
    meeting_title: str = Form(...)
):
    # Save uploaded file
    file_ext = os.path.splitext(file.filename)[1]
    temp_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Convert to WAV mono PCM
    wav_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")
    try:
        convert_to_wav(file_path, wav_path)
    except Exception as e:
        os.remove(file_path)
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )

    # Transcribe audio
    try:
        transcript = transcribe_audio(wav_path)

        # Store in Supabase
        store_transcript(
            client_id=client_id,
            meeting_title=meeting_title,
            audio_url=None,  # replace with actual storage URL if needed
            transcript_text=transcript
        )

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
