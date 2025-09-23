# app/transcription.py
from vosk import Model, KaldiRecognizer
import wave
import json

model = Model("vosk-model-small-en-us-0.15")  # Download from Vosk site

def transcribe_audio(audio_file_path: str):
    wf = wave.open(audio_file_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    final_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            final_text += " " + result.get("text", "")
    final_text += " " + json.loads(rec.FinalResult()).get("text", "")
    return final_text.strip()
