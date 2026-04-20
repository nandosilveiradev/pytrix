import os
import sys

def create_i18n_tuple_logic(name_lower):
    """
    Cria o I18N modular usando Tuplas para garantir a ordem das escolhas
    e chaves mágicas para acesso tipado.
    """
    path = f"pytrix_i18n/pytrix_i18n_{name_lower}.py"
    name_camel = name_lower.capitalize()
    
    content = f"""# Pytrix I18N Modular: {name_camel}

# Tupla Soberana: Define a ordem imutável das escolhas/labels
CHOICES_LABELS = (
    "Iniciar Processo",
    "Configurações",
    "Sair",
)

class PytrixKeys{name_camel}:
    \"\"\"Acessa as chaves pela ordem da tupla (Key Mágica).\"\"\"
    # O índice na tupla é a nossa regra de ouro
    START = 0
    CONFIG = 1
    EXIT = 2
    
    @classmethod
    def get_label(cls, key_index: int) -> str:
        return CHOICES_LABELS[key_index]

# Dicionário de mensagens de apoio
pytrix_i18n_{name_lower} = {{
    "ask_init": f"Selecione uma opção para {name_camel}:",
    "error": "Opção inválida selecionada.",
}}
"""
    if not os.path.exists(path):
        os.makedirs("pytrix_i18n", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"🌐 I18N (Tupla + Keys) criado: {path}")

def pytrix_prefab_mvc(name):
    name_lower = name.lower()
    name_camel = name.capitalize()
    
    create_i18n_tuple_logic(name_lower)

    # Template do Model consumindo a lógica de Tupla
    model_template = f"""from pytrix_models.pytrix_model_base import PytrixModelBase
from pytrix_i18n.pytrix_i18n_{name_lower} import pytrix_i18n_{name_lower}, PytrixKeys{name_camel}, CHOICES_LABELS

class PytrixModel{name_camel}(PytrixModelBase):
    def __init__(self):
        super().__init__()
        self.px_name: str = "PytrixModel{name_camel}"
        
        # Dados do I18N
        self.px_i18n = pytrix_i18n_{name_lower}
        self.px_keys = PytrixKeys{name_camel}
        
        # Referência para o Menu (sempre na ordem da tupla)
        self.px_labels = CHOICES_LABELS
        self.px_bloco = self.px_i18n.get("ask_init")

    def get_choice_text(self, index: int):
        return self.px_keys.get_label(index)
"""

    # ... (Geração de Controller e View mantendo o padrão px_)
    
    model_path = f"pytrix_models/pytrix_model_{name_lower}.py"
    with open(model_path, "w") as f:
        f.write(model_template)
    print(f"✅ Model (Tupla Logic) Forjado: {model_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pytrix_prefab_mvc(sys.argv[1])