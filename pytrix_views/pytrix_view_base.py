from i18n.i18n import I18N
from abc import ABC, abstractmethod

# --- 1. UNIDADE GLOBAL (O CONTRATO) ---
class PytrixI18NProtocol(ABC):
    def __init__(self, px_i18n: dict = I18N):
        self.px_i18n = px_i18n

    @abstractmethod
    def pytrix_get_msg(self, px_key: str) -> str:
        """Contrato: Apenas define o que deve existir."""
        pass

# --- 2. O MOLDE (A LÓGICA DO TRATAMENTO) ---
class PytrixTemplateModel(PytrixI18NProtocol):
    def pytrix_get_msg(self, px_key: str) -> str:
        """Aqui o dado é tratado/recuperado antes da view."""
        return self.px_i18n.get(px_key, px_key)

# --- 3. A HERANÇA DE USO (O GARÇOM DOS DADOS) ---
class PytrixModelBase(PytrixTemplateModel):
    """
    Usa esse cara para os Dumps JSON. 
    Se não tem banco, ele busca no dicionário/dump.
    """
    pass

# --- 4. A VIEW (A ESTETICISTA BURRA) ---
class PytrixView:
    def __init__(self, px_translator: PytrixI18NProtocol):
        # Ela recebe um tradutor que segue o protocolo
        self.px_translator = px_translator

    def pytrix_show_message(self, px_key: str):
        """A View só recebe a chave e 'pinta' na tela."""
        px_msg = self.px_translator.pytrix_get_msg(px_key)
        print(px_msg)

# pytrix_view.py