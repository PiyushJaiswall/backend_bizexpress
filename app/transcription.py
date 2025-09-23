import os
import urllib.request
import zipfile
from vosk import Model, KaldiRecognizer
import wave
import json

MODEL_DIR = "vosk-model-small-en-us-0.15"
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

# Download model if not exists
if not os.path.exists(MODEL_DIR):
    print("Downloading Vosk model...")
    urllib.request.urlretrieve(MODEL_URL, "model.zip")
    print("Extracting model...")
    with zipfile.ZipFile("model.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    os.remove("model.zip")
    print("Model ready!")

model = Model(MODEL_DIR)

def transcribe_audio(file_path: str) -> str:
    wf = wave.open(file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (8000, 16000, 44100):
        raise ValueError("Audio must be WAV mono PCM")

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    result_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += res.get("text", "") + " "

    final_res = json.loads(rec.FinalResult())
    result_text += final_res.get("text", "")
    wf.close()
    return result_text.strip()
