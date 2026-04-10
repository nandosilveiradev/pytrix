# pytrix_models/pytrix_model_base.py
from pytrix_i18n.i18n import I18N

class PytrixModelBase:
    """
    Classe base para modelos Pytrix. 
    Usa o prefixo px_ para garantir fluxo interno rápido e evitar colisões.
    """
    def __init__(self):
        # Identidade e Estado com prefixo px_
        self.px_obj = PytrixModelBase
        self.px_lang: str | None = None
        
        # Atributos PX vinculados diretamente às referências do I18N
        self.px_hello: dict = I18N.get("hello", {})
        self.px_prompt: dict = I18N.get("language_prompt", {}) 
        self.px_arrow: dict = I18N.get("arrow_instructions", {}) 
        self.px_labels: list[str] = I18N.get("language_choices_labels", [])
        self.px_codes: list[str] = I18N.get("language_choices_codes", [])

    def __str__(self):
        return f"PytrixModelBase instance"

    def set_lang(self, choice: str) -> str:
        """Mapeia a label selecionada para o código ISO e define px_lang."""
        mapping = dict(zip(self.px_labels, self.px_codes))
        self.px_lang = mapping.get(choice)
        if not self.px_lang:
            self.px_lang = "pt"  # Fallback seguro
        return self.px_lang

    def get_intro(self) -> str | list[str]:
        """Retorna saudações no idioma atual ou todas as disponíveis."""
        return self.px_hello.get(self.px_lang, list(self.px_hello.values()))

    def get_prompt(self) -> str | list[str]:
        """Retorna o prompt localizado para seleção."""
        return self.px_prompt.get(self.px_lang, list(self.px_prompt.values()))

    def get_arrow(self) -> str | list[str]:
        """Retorna instruções de navegação localizadas."""
        return self.px_arrow.get(self.px_lang, list(self.px_arrow.values()))

    def get_languages(self) -> list[str]:
        """Lista de labels para o menu CLI (Questionary)."""
        return self.px_labels

    def get_localized_text(self, key: str) -> str:
        """Busca qualquer chave no I18N usando o estado px_lang."""
        return I18N.get(key, {}).get(self.px_lang)