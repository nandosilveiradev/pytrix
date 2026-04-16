# Pytrix I18N Modular: --name

# Tupla Soberana: Define a ordem imutável das escolhas/labels
CHOICES_LABELS = (
    "Iniciar Processo",
    "Configurações",
    "Sair",
)

class PytrixKeys--name:
    """Acessa as chaves pela ordem da tupla (Key Mágica)."""
    # O índice na tupla é a nossa regra de ouro
    START = 0
    CONFIG = 1
    EXIT = 2
    
    @classmethod
    def get_label(cls, key_index: int) -> str:
        return CHOICES_LABELS[key_index]

# Dicionário de mensagens de apoio
pytrix_i18n_--name = {
    "ask_init": f"Selecione uma opção para --name:",
    "error": "Opção inválida selecionada.",
}
