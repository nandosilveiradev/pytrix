import subprocess
import time

def iniciar_tunel():
    # Exemplo usando Cloudflared ou Ngrok (ajuste para o seu comando de túnel)
    print("🌐 Subindo o túnel de conexão...")
    comando_tunel = ["cloudflared", "tunnel", "--url", "http://localhost:8080"] 
    
    # Popen não bloqueia o script, ele roda em paralelo
    tunel = subprocess.Popen(comando_tunel, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tunel

if __name__ == "__main__":
    processo_tunel = iniciar_tunel()
    time.sleep(5) # Dá um respiro pro túnel estabilizar
    
    try:
        # Aqui entra sua lógica de rodar a live (o loop que já montamos)
        print("🚀 Rodando script principal...")
        # rodar_bloco_live() 
        
    except KeyboardInterrupt:
        print("\n🛑 Encerrando tudo...")
        processo_tunel.terminate() # Mata o túnel ao sair