#jarvis_stt.py
from faster_whisper import WhisperModel
import speech_recognition as sr

# Modelo 'tiny' para não travar o seu Debian
model = WhisperModel("tiny", device="cpu", compute_type="int8")

def ouvir_jarvis():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Jarvis ouvindo...")
        audio = r.listen(source)
    
    # Salva na RAM (/dev/shm) pra ser voador
    with open("/dev/shm/voice.wav", "wb") as f:
        f.write(audio.get_wav_data())

    segments, _ = model.transcribe("/dev/shm/voice.wav")
    return " ".join([s.text for s in segments])