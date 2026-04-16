import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Pytrix Sovereign API")

# Caminho absoluto da raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Onde os arquivos do Matrix (HTML/CSS) estão
STATIC_DIR = os.path.join(BASE_DIR, "pytrix_web_static")

# Serve a pasta para assets (imagens, js, css)
# Importante: o primeiro "/static" é o prefixo na URL, o segundo é o diretório
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    # Entrega o index.html que está lá dentro
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/bip")
async def play_bip():
    # Executa o seu binário 'bip' que está na raiz
    os.system(os.path.join(BASE_DIR, "bip"))
    return {"status": "Bip executado com sucesso!"}