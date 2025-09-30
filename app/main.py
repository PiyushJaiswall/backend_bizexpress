from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
import uuid
import ffmpeg
import logging
import traceback

# --- Configure logging globally ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Import your application modules ---
from app.transcription import transcribe_audio
from app.supabase_client import store_transcript

# --- Initialize FastAPI App ---
app = FastAPI(title="BizExpress Backend", version="1.0.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def convert_to_wav(input_path: str, output_path: str):
    logger.info(f"STARTING CONVERSION: Converting {input_path} to {output_path}")
    try:
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, format='wav', ac=1, ar=16000)
        stream = ffmpeg.overwrite_output(stream)
        
        stdout, stderr = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        
        if stdout:
            logger.info("ffmpeg stdout: " + stdout.decode())
        if stderr:
            logger.warning("ffmpeg stderr: " + stderr.decode())
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("Conversion resulted in an empty or non-existent file.")
            
        logger.info(f"CONVERSION SUCCESS: Output file size is {os.path.getsize(output_path)} bytes.")

    except ffmpeg.Error as e:
        logger.error("FFMPEG FAILED: " + e.stderr.decode())
        raise Exception(f"ffmpeg execution failed: {e.stderr.decode()}")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/transcribe/")
async def transcribe(
    file: UploadFile = File(...),
    client_id: str = Form(...),
    meeting_title: str = Form(...)
):
    file_path = None
    wav_path = None
    try:
        logger.info(f"Received file upload: {file.filename}")
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".webm"
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, temp_filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"File saved to {file_path}, size: {len(content)} bytes")
        if len(content) == 0:
            raise Exception("Uploaded file is empty.")

        wav_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")
        convert_to_wav(file_path, wav_path)

        logger.info("Starting transcription...")
        transcript = transcribe_audio(wav_path)
        logger.info(f"Transcription result: '{transcript}'")

        if not transcript:
             logger.warning("Transcription is empty. Audio may have been silent.")

        logger.info("Storing transcript in Supabase...")
        store_transcript(
            client_id=client_id,
            meeting_title=meeting_title,
            audio_url=None,
            transcript_text=transcript
        )
        logger.info("Successfully stored in Supabase.")

        return {"status": "success", "transcript": transcript}

    except Exception as e:
        logger.error("!!!!!! AN UNHANDLED EXCEPTION OCCURRED !!!!!!")
        logger.error(f"Error of type {type(e).__name__}: {e}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An internal server error occurred.", "detail": str(e)}
        )
    finally:
        logger.info("Cleaning up temporary files...")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
        logger.info("Cleanup complete.")
