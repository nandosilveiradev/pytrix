from pytrix_models.pytrix_model_base import PytrixModelBase
from pytrix_i18n.pytrix_i18n_--name import pytrix_i18n_--name, PytrixKeys--name, CHOICES_LABELS

class PytrixModel--name(PytrixModelBase):
    def __init__(self):
        super().__init__()
        self.px_name: str = "PytrixModel--name"
        
        # Dados do I18N
        self.px_i18n = pytrix_i18n_--name
        self.px_keys = PytrixKeys--name
        
        # Referência para o Menu (sempre na ordem da tupla)
        self.px_labels = CHOICES_LABELS
        self.px_bloco = self.px_i18n.get("ask_init")

    def get_choice_text(self, index: int):
        return self.px_keys.get_label(index)
