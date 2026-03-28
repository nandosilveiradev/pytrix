from models.model_base import ModelBase, I18N


class ModelSelectLanguage(ModelBase):
    def __init__(self):
        super().__init__() 
        self.lang: str | None = None
        self.bloco: str = I18N["bloco"]
        self.hello: dict = I18N["hello"]
        self.prompt: dict = I18N["language_prompt"]
        self.arrow: dict = I18N["arrow_instructions"]
        self.codes: list[str] = I18N["language_choices_codes"]
        self.labels: list[str] = I18N["language_choices_labels"]

   
        