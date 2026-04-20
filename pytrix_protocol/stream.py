import os
import subprocess
import time
import requests

# --- CONFIGURAÇÕES TÉCNICAS ---
SERVER_URL = "rtmps://live-api-s.facebook.com:443/rtmp/"
STREAM_KEY = "SUA_CHAVE_AQUI"
ACCESS_TOKEN = "SEU_PAGE_ACCESS_TOKEN"
LIVE_VIDEO_ID = "ID_DA_SUA_LIVE" # Obtido ao iniciar a live no Painel

# --- MAPA DE CONTEÚDO (Pastas, Títulos e SEO) ---
# O script vai rodar cada pasta por um ciclo completo e mudar o título
BLOCOS = [
    {
        "pasta": "videos/jeans",
        "prefixo_titulo": "TV DUE - Olhem esses {qtd} modelos de CALÇAS em promoção!",
        "desc": "Calça Jeans Plus Size em Jacareí. WhatsApp na Bio!"
    },
    {
        "pasta": "videos/bodys",
        "prefixo_titulo": "TV DUE - Confira {qtd} modelos de BODYS e Blusas agora!",
        "desc": "Moda Feminina Plus Size. Entrega em Jacareí e região."
    },
    {
        "pasta": "videos/kids",
        "prefixo_titulo": "TV DUE - Coleção KIDS: {qtd} looks para os pequenos!",
        "desc": "Moda Infantil na Due. Qualidade e preço justo."
    }
]

def atualizar_seo_facebook(titulo, descricao):
    """Atualiza o título e descrição da Live via API Graph"""
    url = f"https://graph.facebook.com/v19.0/{LIVE_VIDEO_ID}"
    payload = {
        'title': titulo,
        'description': descricao,
        'access_token': ACCESS_TOKEN
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print(f"📢 SEO Atualizado: {titulo}")
        else:
            print(f"⚠️ Erro API FB: {r.text}")
    except Exception as e:
        print(f"❌ Falha na conexão com API: {e}")

def gerar_lista(caminho_pasta):
    arquivos = [f for f in os.listdir(caminho_pasta) if f.endswith('.mp4')]
    arquivos.sort()
    with open("lista.txt", "w") as f:
        for video in arquivos:
            f.write(f"file '{caminho_pasta}/{video}'\n")
    return len(arquivos)

def rodar_bloco(bloco):
    qtd = gerar_lista(bloco["pasta"])
    titulo_dinamico = bloco["prefixo_titulo"].format(qtd=qtd)
    
    # 1. Atualiza o título no Facebook antes de começar o vídeo
    atualizar_seo_facebook(titulo_dinamico, bloco["desc"])
    
    # 2. Comando FFmpeg para rodar a lista daquela pasta uma vez
    comando = [
        'ffmpeg', '-re', '-f', 'concat', '-safe', '0', '-i', 'lista.txt',
        '-c', 'copy', '-f', 'flv', f"{SERVER_URL}{STREAM_KEY}"
    ]
    
    print(f"🎬 Iniciando bloco: {bloco['pasta']} ({qtd} vídeos)")
    subprocess.run(comando)

if __name__ == "__main__":
    while True:
        for bloco in BLOCOS:
            try:
                rodar_bloco(bloco)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                print(f"🔥 Erro no loop: {e}")
                time.sleep(10)