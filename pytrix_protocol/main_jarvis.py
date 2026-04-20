import jarvis_stt
import pytrix_core
import jarvis_speaker
import time

def start_jarvis():
    jarvis_speaker.falar("Sistema Jarvis iniciado no root. Pode falar, Fernando.")
    
    while True:
        try:
            # 1. Ouve o que você diz
            comando_voz = jarvis_stt.ouvir_jarvis()
            print(f"Você disse: {comando_voz}")
            
            if "descansar" in comando_voz.lower():
                jarvis_speaker.falar("Indo para o modo de espera. Até mais, patrão.")
                break
            
            # 2. Processa com o Ollama e salva com a lógica do Tail
            jarvis_speaker.falar("Processando código...")
            nome_gerado = pytrix_core.processar_comando(comando_voz)
            
            # 3. Dá o feedback
            jarvis_speaker.falar(f"Arquivo {nome_gerado} gerado com sucesso.")
            
        except Exception as e:
            print(f"Erro no loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_jarvis()