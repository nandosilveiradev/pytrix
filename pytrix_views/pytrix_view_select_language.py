# pytrix_views/pytrix_view_select_language.py
from pytrix_views.pytrix_view_base import PytrixViewBase

class PytrixViewSelectLanguage(PytrixViewBase):
    """
    Interface para seleção de idioma do ecossistema Pytrix.
    Usa o padrão px_ para otimização de busca no LSP e Tabnine.
    
    Herda de: PytrixViewBase
    Métodos Disponíveis:
        - show_message(message: str) -> str
        - show_error(error: str) -> str
        - show_success(success: str) -> str
        - show_menu(options: list, prompt: str) -> str
        - show_value(msg: str) -> None
    """
    def __init__(self):
        super().__init__()
        # Identificador px_ para rastreabilidade e auditoria rápida
        self.px_name: str = "PytrixViewSelectLanguage"
        
        # Se houver estados específicos da View, use o prefixo px_
        # Exemplo: self.px_stats = True (herdado ou local)

    # A View permanece "burra", herdando a lógica de exibição da Base,
    # mas agora devidamente identificada no ecossistema Pytrix.