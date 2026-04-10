# pytrix_models/pytrix_model_select_language.py
from pytrix_models.pytrix_model_base import PytrixModelBase

class PytrixModelSelectLanguage(PytrixModelBase):
    """
    Modelo especializado na gestão de idiomas do ecossistema Pytrix.
    Utiliza o padrão px_ para otimização de fluxo interno e indexação via LSP.
    
    Herda de: PytrixModelBase
    """
    def __init__(self):
        # Inicializa a base que já prepara o acesso ao I18N
        super().__init__() 
        
        # Identificador de classe para auditoria de estado
        self.px_name: str = "PytrixModelSelectLanguage"
        
        # Estado local de idioma (ISO Code)
        self.px_lang: str | None = None
        
        # Importação local do I18N para mapeamento das chaves do Prefab
        from pytrix_i18n.i18n import I18N
        
        # Mapeamento para o namespace px_ (acesso ultra-rápido por referência)
        self.px_bloco: str = I18N.get("bloco", "Pytrix_Default_Block")
        self.px_hello: dict = I18N.get("hello", {})
        self.px_prompt: dict = I18N.get("language_prompt", {})
        self.px_arrow: dict = I18N.get("arrow_instructions", {})
        self.px_codes: list[str] = I18N.get("language_choices_codes", [])
        self.px_labels: list[str] = I18N.get("language_choices_labels", [])

    # Os métodos get_intro, get_prompt, etc., herdados da Base 
    # já utilizam esses atributos px_ internamente.