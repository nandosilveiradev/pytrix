# pytrix_views/pytrix_view_base.py
import questionary

class PytrixViewBase:
    """
    Classe base para todas as Views do ecossistema Pytrix.
    Centraliza a interação CLI e padroniza o namespace px_.
    """
    def __init__(self):
        # Atributo de estado global do framework
        self.px_stats: bool = True
        # Identificador base para auditoria
        self.px_base_name: str = "PytrixViewBase"

    def show_message(self, message: str) -> str:
        """Retorna uma mensagem genérica formatada."""
        return message

    def show_error(self, error: str) -> str:
        """Retorna uma mensagem de erro padronizada Pytrix."""
        return f"[ERRO] {error}"

    def show_success(self, success: str) -> str:
        """Retorna uma mensagem de sucesso padronizada Pytrix."""
        return f"[OK] {success}"

    def show_menu(self, options: list, prompt: str) -> str:
        """
        Gera um menu interativo usando questionary.
        Otimizado para o fluxo do Controller via self.px_view.
        """
        choice = questionary.select(
            prompt,
            choices=options
        ).ask()
        return choice

    def show_value(self, msg: str) -> None:
        """
        Único ponto de saída de impressão direta no console.
        Facilita o redirecionamento de logs ou auditoria de saída.
        """
        print(f"{msg}")