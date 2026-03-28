# models/model_base.py
from i18n.i18n import I18N

class ModelBase:
    def __init__(self):
        self.obj = ModelBase
        self.lang: str | None = None
        # --- CORREÇÃO: Inicialize os atributos que os métodos get_* usam ---
        self.hello: dict = I18N.get("hello", {})
        # Assumindo estas são as chaves corretas no seu dicionário I18N
        self.prompt: dict = I18N.get("language_prompt", {}) 
        self.arrow: dict = I18N.get("arrow_instructions", {}) 
        self.labels: list[str] = I18N.get("language_choices_labels", [])
        self.codes: list[str] = I18N.get("language_choices_codes", [])
        # ----------------------------------------------------------------

    def __str__(self):
        return f"ModelBase instance"

    def set_lang(self, choice: str) -> str:
        mapping = dict(zip(self.labels, self.codes))
        self.lang = mapping.get(choice)
        if not self.lang:
            self.lang = "pt"  # fallback padrão
        return self.lang

    def get_intro(self) -> str | list[str]:
        """Mensagem de boas-vindas no idioma escolhido ou todas se não definido."""
        return self.hello.get(self.lang, list(self.hello.values()))

    def get_prompt(self) -> str | list[str]:
        """Prompt de seleção de idioma."""
        return self.prompt.get(self.lang, list(self.prompt.values()))

    def get_arrow(self) -> str | list[str]:
        """Instruções de navegação."""
        # Isso agora funcionará porque self.arrow existe e é um dicionário
        return self.arrow.get(self.lang, list(self.arrow.values()))

    def get_languages(self) -> list[str]:
        """Lista de labels disponíveis para escolha."""
        return self.labels

    # Mantive o get_text() adicionado, pois ele é útil para a modularidade
    def get_localized_text(self, key: str) -> str:
        """
        Retorna o texto localizado para a chave I18N usando self.lang.
        Assume que self.lang está definido e a chave existe no I18N.
        """
        # Acesso direto, confiando na integridade dos dados e do fluxo.
        return I18N.get(key, {}).get(self.lang)
