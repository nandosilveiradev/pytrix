import subprocess
import os
import re

def processar_comando(comando_usuario):
    ollama_bin = "/usr/local/bin/ollama"
    
    # --- O ENVELOPE (A MÁGICA) ---
    # Adicionamos as regras rígidas antes e depois do que você disse
    prefixo = "Gere apenas o código puro em Python. Não explique nada, não diga 'Aqui está', não use markdown. "
    sufixo = " . Na última linha, escreva apenas o nome do arquivo com extensão .py (exemplo: script.py)."
    
    prompt_final = f"{prefixo} {comando_usuario} {sufixo}"
    
    # Chamada do Ollama
    cmd = [ollama_bin, "run", "llama3", prompt_final]
    
    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, check=True)
        out = resultado.stdout
        
        # Limpeza de possíveis blocos de markdown que a IA teime em usar
        clean_out = out.replace("```python", "").replace("```", "").strip()
        linhas = [l for l in clean_out.split('\n') if l.strip()]
        
        if not linhas:
            return "erro_vazio.py"
            
        # Pega o nome na última linha (usando regex para garantir que pegamos só o nome.py)
        ultima_linha = linhas[-1].strip()
        match = re.search(r'([\w-]+\.py)', ultima_linha)
        nome_arquivo = match.group(1) if match else "script_gerado.py"
        
        # O conteúdo é tudo menos a última linha
        conteudo = "\n".join(linhas[:-1])
        
        # Salvando no diretório padrão
        os.makedirs("/root/projetos", exist_ok=True)
        caminho = os.path.join("/root/projetos", nome_arquivo)
        
        with open(caminho, "w") as f:
            f.write(conteudo)
            
        return nome_arquivo

    except Exception as e:
        print(f"Erro interno no Pytrix Core: {e}")
        return None