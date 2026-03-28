from views.view_base import ViewBase

class ViewSelectLanguage(ViewBase):
    def __init__(self):
        super().__init__()  # chama o construtor da base
        self.name: str  = "ViewSelectLanguage"

        # Métodos herdados da views/ViewBase:
        # - show_message(message: str) -> str
        # - show_error(error: str) -> str
        # - show_success(success: str) -> str
        # - show_menu(languages: list, prompt: str) -> str
        # - show_value(msg: str) -> None

    # Se não sobrescrever, herdará direto da views/ViewBase

    