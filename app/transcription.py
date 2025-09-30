import whisper
import os

# Load the Whisper model. This will download the model on the first run.
# 'base.en' is a great balance of speed and accuracy for a free tier.
model = whisper.load_model("tiny.en")

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an audio file using OpenAI's Whisper model.
    """
    if not os.path.exists(file_path):
        # This check is good practice
        raise FileNotFoundError(f"Audio file not found at {file_path}")

    # The transcribe function handles everything from loading audio to processing
    result = model.transcribe(file_path, fp16=False) # Use fp16=False for CPU-only servers

    # The transcribed text is in the 'text' key of the result dictionary
    return result.get("text", "").strip()


