# /root/pytrix/pytrix_views/pytrix_view_base.py
from typing import Protocol, runtime_checkable, List
import questionary

@runtime_checkable
class PytrixViewBaseProtocol(Protocol):
    """
    ANARQUIA: O contrato para qualquer View Pytrix.
    Se tem esses métodos, a máquina aceita.
    """
    px_stats: bool
    px_base_name: str

    def show_message(self, message: str) -> str: ...
    def show_error(self, error: str) -> str: ...
    def show_success(self, success: str) -> str: ...
    def show_menu(self, options: List[str], prompt: str) -> str: ...
    def show_value(self, msg: str) -> None: ...

class PytrixViewBase(PytrixViewBaseProtocol):
    """
    O TEMPLATE: Implementação oficial e produtiva.
    """
    def __init__(self):
        self.px_stats = True
        self.px_base_name = "PytrixViewTemplate"

    def show_message(self, message: str) -> str:
        return message

    def show_error(self, error: str) -> str:
        return f"[ERRO] {error}"

    def show_success(self, success: str) -> str:
        return f"[OK] {success}"

    def show_menu(self, options: list, prompt: str) -> str:
        # A interatividade que acelera o dev
        choice = questionary.select(
            prompt,
            choices=options
        ).ask()
        return choice

    def show_value(self, msg: str) -> None:
        # Único ponto de saída real
        print(f"{msg}")