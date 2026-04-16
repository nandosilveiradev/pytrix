import os
import ollama
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Pytrix Sovereign API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "pytrix_web_static")

class ChatRequest(BaseModel):
    prompt: str

# --- 1. ROTAS DE API PRIMEIRO ---

@app.post("/api/chat")
async def chat_with_pytrix(request: ChatRequest):
    try:
        # Injetando a real identidade para acabar com a alucinação
        system_prompt = (
            "Você é a IA do ecossistema Pytrix. Seu criador é Fernando Silveira, "
            "Senior Fullstack Developer e CTO da WebSolutionsFS em Jacareí-SP. "
            "Ele é especialista em Python (FastAPI, MoviePy), Debian e automação de vídeo. "
            "Responda de forma técnica e realística, sem inventar que ele é ministro ou influencer."
        )
        
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': request.prompt},
        ])
        return {"response": response['message']['content']}
    except Exception as e:
        return {"error": str(e)}

@app.get("/bip")
async def play_bip():
    os.system(os.path.join(BASE_DIR, "bip"))
    return {"status": "Bip executado!"}

# --- 2. ROTA DA PÁGINA INICIAL DEPOIS ---

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# --- 3. MOUNT POR ÚLTIMO ---

# Isso garante que imagens e CSS funcionem sem quebrar as rotas acima
app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")