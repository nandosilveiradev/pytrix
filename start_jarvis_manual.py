import sys
import os

# Força o Python a olhar dentro da pasta pytrix_core para achar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'pytrix_core')))

try:
    from pytrix_core import pytrix_core
except ImportError:
    # Caso o import direto falhe pela estrutura de pastas
    import pytrix_core

SHM_PATH = "/dev/shm/pytrix_buffer.py"

def ler_codigo_da_ram():
    """Lê o código atual que está sendo editado na memória compartilhada."""
    if os.path.exists(SHM_PATH):
        try:
            with open(SHM_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""

def executar():
    # 1. Carrega o contexto global (all.py)
    contexto = ""
    if os.path.exists("all.py"):
        try:
            # Pegamos apenas os últimos 500kb se o arquivo for absurdo, 
            # para evitar lentidão extrema na API local.
            tamanho_max = 500 * 1024 
            with open("all.py", "r", encoding="utf-8") as f:
                contexto = f.read()
                if len(contexto) > tamanho_max:
                    contexto = contexto[-tamanho_max:] # Pega a parte final (mais recente)
        except Exception as e:
            contexto = f"Erro ao ler contexto: {e}"

    # Modo de comando único via terminal
    if len(sys.argv) > 1:
        comando = " ".join(sys.argv[1:])
        print(f"🚀 Pytrix a processar: {comando}")
        resultado = pytrix_core.processar_comando(comando, context=contexto)
        if resultado:
            print(f"✅ Sucesso! Ficheiro '{resultado}' gerado.")
        return

    # Modo Interativo (Jarvis)
    print("⌨️  Pytrix Framework - MODO JARVIS ATIVO")
    print("---------------------------------------")
    
    while True:
        try:
            # 2. Captura o que está no editor agora
            codigo_atual = ler_codigo_da_ram()
            
            cmd = input("\n🤖 Digite o comando (ou Enter p/ atualizar): ")
            
            if not cmd.strip():
                continue

            if cmd.lower() in ['sair', 'exit', 'quit']: 
                print("👋 Jarvis encerrando...")
                break
            
            # 3. Monta o Super Prompt
            prompt_final = (
                "SISTEMA: Você é o JARVIS do framework PYTRIX.\n"
                f"ESTRUTURA DO PROJETO:\n{contexto}\n\n"
                f"CÓDIGO ATUAL NO EDITOR:\n{codigo_atual}\n\n"
                f"MISSÃO: {cmd}"
            )
            
            print(f"🔎 Analisando com Llama 3 (via API)...")
            
            # 4. Envia para o core (que deve usar requests agora)
            resultado = pytrix_core.processar_comando(cmd, context=prompt_final)
            
            if resultado:
                # O core já salva em /root/projetos, aqui apenas confirmamos
                print(f"✅ Gerado com sucesso: {resultado}")
            else:
                print("⚠️  O motor não retornou um arquivo válido.")
                
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro no loop Jarvis: {e}")

if __name__ == "__main__":
    executar()