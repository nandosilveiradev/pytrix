# pyprefab_components.py (Raiz do projeto)

def generate_column(span=1, content=""):
    """Gera uma div de coluna baseada no grid de 12"""
    # Ex: span 3 = 25% da tela (estilo Photoshop)
    return f'<div style="grid-column: span {span} / span {span};">{content}</div>'

def generate_h1(text, classes=""):
    """Componente H1 com padrão GitHub (Primer Design)"""
    # Borda inferior fina e espaçamento clássico do GitHub
    return f'<h1 class="text-2xl font-semibold border-b border-[#d0d7de] pb-2 mb-4 {classes}">{text}</h1>'

# Exemplo de chamada via CLI no Debian:
# python3 pyprefab_components.py --h1 "Configurações de Idioma"

