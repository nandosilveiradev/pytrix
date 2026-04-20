import argparse

def px_check_and_prefix(name, prefix):
    """
    Evita a duplicação de prefixos (ex: impede pytrix_pytrix_funcao)
    """
    if name.startswith(prefix):
        return name
    return f"{prefix}{name}"

def px_generate_prompt(mode, custom_name=None):
    # Definindo as regras de ouro
    v_pre = "px_"
    f_pre = "pytrix_"
    c_pre = "Pytrix"

    prompt = f"""
[SISTEMA: ENGINE REFINERY V1 - REGRAS DE NOMENCLATURA]
Você deve refatorar ou criar o código seguindo RIGOROSAMENTE estas tags:

1. FUNÇÕES: Prefixo '{f_pre}' (Ex: {f_pre}iniciar_motor). 
   ⚠️ CUIDADO: Se a função já começar com '{f_pre}', não duplique.
2. VARIÁVEIS: Prefixo '{v_pre}' (Ex: {v_pre}buffer_data).
   ⚠️ CUIDADO: Se a variável já começar com '{v_pre}', não duplique.
3. CLASSES: Prefixo '{c_pre}' (Ex: {c_pre}Core). 
   ⚠️ CUIDADO: Não use {c_pre}{c_pre}.

SAÍDA OBRIGATÓRIA:
<pytrix_contexto filename="{f_pre}contexto.py">
[CÓDIGO DESTILADO]
</pytrix_contexto>

Nota: Não use Markdown. Use apenas os prefixos solicitados.
"""
    return prompt

# ... (resto do código do script permanece igual)