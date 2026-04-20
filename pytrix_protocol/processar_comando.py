import re
import os
import subprocess

def processar_pytrix_contexto(resposta_ia):
    # Regex atualizada para o novo padrão: pytrix_contexto
    padrao = r'<pytrix_contexto filename="(.*?)">(.*?)</pytrix_contexto>'
    
    # re.DOTALL é o que permite pegar o código com múltiplas linhas
    matches = re.finditer(padrao, resposta_ia, re.DOTALL)
    
    arquivos_gerados = []

    for match in matches:
        filename = match.group(1).strip()
        conteudo = match.group(2).strip()
        
        # Salvando na pasta core (ajuste o caminho se necessário)
        caminho_saida = os.path.join("../pytrix_core", filename)
        
        try:
            with open(caminho_saida, "w") as f:
                f.write(conteudo)
            
            print(f"✅ [CONTEXTO] Arquivo '{filename}' destilado com sucesso.")
            arquivos_gerados.append(caminho_saida)
            
            # Se for um script, já garante a permissão de execução
            if filename.endswith(('.sh', '.py')):
                os.chmod(caminho_saida, 0o755)

        except Exception as e:
            print(f"❌ [ERRO] Falha ao salvar {filename}: {e}")

    # --- O TOQUE FINAL: O BIP ---
    if arquivos_gerados:
        # Tenta rodar o seu binário 'bip' para avisar que terminou
        try:
            # Roda o bip que está na pasta atual do protocolo
            subprocess.run(["./bip"], check=False)
        except:
            print("🔔 [AVISO] Processamento concluído (bip falhou ou não encontrado).")
    else:
        print("⚠️ [AVISO] Nenhuma tag <pytrix_contexto> identificada.")

# Exemplo de chamada:
# processar_pytrix_contexto(output_do_jarvis)