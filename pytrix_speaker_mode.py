from faster_whisper import WhisperModel
import speech_recognition as sr

# Carrega o modelo (o 'tiny' é instantâneo para comandos de voz)
model_size = "tiny"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def ouvir_jarvis():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Jarvis ouvindo...")
        audio = r.listen(source)
        
    # Salva o áudio temporariamente na RAM (/dev/shm) para ser rápido
    with open("/dev/shm/temp_audio.wav", "wb") as f:
        f.write(audio.get_wav_data())

    segments, _ = model.transcribe("/dev/shm/temp_audio.wav", beam_size=5)
    texto = " ".join([segment.text for segment in segments])
    return texto

# Agora é só jogar o 'texto' para a função do Pytrix que a gente criou!