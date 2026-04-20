import json
import time
import subprocess
import random
import os

# Caminho do arquivo gerado pelo minerador
LEADS_PATH = "/root/pytrix/pytrix_tmp/leads_quentes.json"

def obter_temp_log():
    """Lê a temperatura para o log do terminal"""
    try:
        if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return f"{int(f.read().strip()) / 1000.0}°C"
    except: pass
    return "N/A"

def enviar_sms_adb(numero, mensagem):
    """Dispara o SMS via Android (Root/USB)"""
    try:
        # Prepara o intent de SMS no Android
        msg_limpa = mensagem.replace('"', '\\"')
        cmd = f'adb shell am start -a android.intent.action.SENDTO -d sms:{numero} --es sms_body "{msg_limpa}" --ez exit_on_sent true'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Tempo para o app carregar no celular
        time.sleep(3)
        
        # Simula o envio (Sequência padrão: foca no botão e dá enter)
        subprocess.run('adb shell input keyevent 22', shell=True) # Seta p/ Direita
        subprocess.run('adb shell input keyevent 66', shell=True) # Enter
        return True
    except Exception as e:
        print(f"❌ Erro de Hardware: {e}")
        return False

def main():
    if not os.path.exists(LEADS_PATH):
        print("⚠️ Arquivo de leads não encontrado!")
        return

    with open(LEADS_PATH, "r", encoding="utf-8") as f:
        leads = json.load(f)

    print(f"🚀 Iniciando Prospecção B2B. {len(leads)} empresas na fila.")

    for lead in leads:
        empresa = lead.get('empresa', 'Empresa')
        # Certifique-se que o minerador salvou o campo 'telefone'
        telefone = lead.get('telefone', '') 

        if not telefone:
            continue

        # --- TUA MENSAGEM CUSTOMIZADA ---
        # Foco: Olá [Nome], vi que [Empresa] não tem site, ofereço Dev/SEO
        msg = f"Ola, vi que a {empresa} nao tem site cadastrado no Google. Sou Desenvolvedor e especialista em SEO. Posso te ajudar a aparecer primeiro nas buscas. Se tiver interesse, me chama no Whats!"

        t_atual = obter_temp_log()
        print(f"📩 [{t_atual}] Enviando para: {empresa}...")

        if enviar_sms_adb(telefone, msg):
            # O intervalo seguro que definimos (30s a 2min)
            espera = random.randint(30, 120)
            print(f"✅ Enviado com sucesso. Próximo em {espera}s.")
            time.sleep(espera)
        else:
            print(f"🛑 Falha ao processar {empresa}. Verifique o cabo USB.")

if __name__ == "__main__":
    # Inicia o servidor ADB no Debian
    os.system("adb start-server")
    main()