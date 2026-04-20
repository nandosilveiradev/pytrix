import os

def gerar_dump():
    base_path = "/root/pytrix"
    output_file = "/root/pytrix/all.py"
    
    # Lista de pastas que queremos mapear para o Jarvis
    pastas_alvo = ['pytrix_core', 'pytrix_models', 'pytrix_views', 'pytrix_utils']
    
    with open(output_file, "w") as out:
        out.write("# DUMP COMPLETO DO FRAMEWORK PYTRIX - CONTEXTO PARA IA\n\n")
        
        for root, dirs, files in os.walk(base_path):
            # Filtra apenas as pastas do projeto
            if any(folder in root for folder in pastas_alvo):
                for file in files:
                    if file.endswith(".py") or file.endswith(".c") or file.endswith(".h"):
                        filepath = os.path.join(root, file)
                        out.write(f"\n# {'='*20}\n# ARQUIVO: {filepath}\n# {'='*20}\n\n")
                        try:
                            with open(filepath, "r") as f:
                                out.write(f.read())
                                out.write("\n")
                        except Exception as e:
                            out.write(f"# Erro ao ler arquivo: {e}\n")

    print(f"✅ Contexto atualizado com sucesso em: {output_file}")

if __name__ == "__main__":
    gerar_dump()