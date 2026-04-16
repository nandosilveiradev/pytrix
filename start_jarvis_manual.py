import sys
import pytrix_core

def executar():
    """
    Interface CLI para o Pytrix. 
    Suporta comandos diretos por argumentos ou modo interativo.
    """
    if len(sys.argv) > 1:
        # Modo Argumentos (Direto do Shell)
        comando = " ".join(sys.argv[1:])
        print(f"🚀 Pytrix a processar pedido: {comando}")
        resultado = pytrix_core.processar_comando(comando)
        if resultado:
            print(f"✅ Sucesso! Ficheiro '{resultado}' gerado em /root/projetos/")
    else:
        # Modo Interativo
        print("⌨️ Pytrix Framework - Modo Manual (Digite 'sair' para encerrar)")
        while True:
            try:
                cmd = input("\n🤖 Digite o comando: ")
                if cmd.lower() in ['sair', 'exit', 'quit']:
                    print("👋 Encerrando Pytrix...")
                    break
                
                if not cmd.strip():
                    continue
                    
                print(f"🔎 Processando...")
                resultado = pytrix_core.processar_comando(cmd)
                if resultado:
                    print(f"✅ Gerado: {resultado}")
                else:
                    print("❌ Falha na geração.")
                    
            except KeyboardInterrupt:
                print("\nInterrompido pelo utilizador.")
                break

if __name__ == "__main__":
    executar()