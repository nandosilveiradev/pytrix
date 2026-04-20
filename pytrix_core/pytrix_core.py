import os
import requests
import json

def processar_comando(prompt, context=None):
    # O contexto aqui vai levar o conteúdo do all.py que tem toda essa árvore aí
    corpo_do_prompt = context if context else prompt
    
    regra_ouro = (
        "\n\nCONTEXTO DO FRAMEWORK: Você é o JARVIS integrado ao PYTRIX. "
        "Use a árvore de diretórios e o all.py para entender as dependências. "
        "Responda APENAS com o código completo. "
        "Última linha: o nome do arquivo começando com pytrix_."
    )

    prompt_final = corpo_do_prompt + regra_ouro

    # Ollama API local
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": prompt_final,
        "stream": False
    }

    try:
        # Timeout longo porque o all.py é gigante
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        res_json = response.json()
        out = res_json.get("response", "")
        
        # Sanitização de Markdown
        linhas = [l for l in out.replace("```python", "").replace("```", "").split('\n') if l.strip()]
        
        if not linhas: return None

        # Pega o nome do arquivo (última linha)
        nome_arquivo = linhas[-1].strip()
        if "pytrix_" not in nome_arquivo:
            nome_arquivo = "pytrix_generated_output.py"
            conteudo = "\n".join(linhas)
        else:
            conteudo = "\n".join(linhas[:-1])

        # Organização na sua estrutura
        os.makedirs("/root/projetos", exist_ok=True)
        caminho = os.path.join("/root/projetos", nome_arquivo)
        
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
            
        return nome_arquivo
    except Exception as e:
        print(f"❌ Falha no motor Pytrix: {e}")
        return None