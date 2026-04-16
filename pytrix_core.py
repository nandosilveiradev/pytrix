import os
import subprocess

def processar_comando(prompt):
    # O teu prompt técnico + a tua regra de ouro
    prompt = prompt + (
        " monte um model de template que busca msg em um arquivo no modulo i18.i18n import I18N "
        "que é um dicionário com base na chave digitada, como protocol, depois crie um arquivo "
        "PytrixModelBase que herda esse protocolo. "
        "regra não use comentários ou fale qualquer coisa, não preciso da sua eplicação apenas "
        "mostre o que pedi, sem ser educado ou falar qualquer coisa. apenas coloque o código e "
        "o nome do arquivo no final com base no que foi descrito da funcionalidade, pare de "
        "comentar está atrapalhando nao quero que vc interaja só faça o pedido e na ultima linha "
        "coloque o nome para o arquivo.py com base no conteúdo pedido coloque pytrix_ no começo "
        "da sua sugestão de nome deixe na ultima linha"
    )

    ollama_bin = "/usr/local/bin/ollama"
    cmd = [ollama_bin, "run", "llama3", prompt]
    
    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        out = resultado.stdout
        linhas = [l for l in out.strip().split('\n') if l.strip()]
        
        if not linhas:
            return None

        ultima_linha = linhas[-1].strip()
        
        # Filtro Anti-Erro (o teu original funcional)
        if " " in ultima_linha or "(" in ultima_linha or ":" in ultima_linha:
            nome_arquivo = "pytrix_script_gerado.py"
            conteudo = "\n".join(linhas).replace("```python", "").replace("```", "").strip()
        else:
            nome_arquivo = ultima_linha
            conteudo = "\n".join(linhas[:-1]).replace("```python", "").replace("```", "").strip()

        os.makedirs("/root/projetos", exist_ok=True)
        caminho_final = os.path.join("/root/projetos", nome_arquivo)
        
        with open(caminho_final, "w", encoding="utf-8") as f:
            f.write(conteudo)
            
        return nome_arquivo

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None