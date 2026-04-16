# /root/pytrix/pytrix_models/pytrix_model_base.py
import os
from typing import Protocol, runtime_checkable, List, Dict, Any, Union
from pytrix_i18n.i18n import I18N

@runtime_checkable
class PytrixModelProtocol(Protocol):
    """
    O CONTRATO TOTAL: Define a soberania do modelo.
    Se não tiver TUDO isso, não é um modelo Pytrix.
    """
    px_obj: type
    px_lang: Union[str, None]
    px_env: str
    px_hello: Dict[str, Any]
    px_prompt: Dict[str, Any]
    px_arrow: Dict[str, Any]
    px_labels: List[str]
    px_codes: List[str]

    def px_locate(self) -> str: ...
    def set_lang(self, choice: str) -> str: ...
    def get_intro(self) -> Union[str, List[str]]: ...
    def get_prompt(self) -> Union[str, List[str]]: ...
    def get_arrow(self) -> Union[str, List[str]]: ...
    def get_languages(self) -> List[str]: ...
    def get_localized_text(self, key: str) -> str: ...

class PytrixModelBase(PytrixModelProtocol):
    """
    A IMPLEMENTAÇÃO MESTRE: Herda o protocolo em nada (completa).
    """
    def __init__(self):
        # Identidade e Localização Global
        self.px_obj = self.__class__
        self.px_env = self.px_locate()
        self.px_lang = None
        
        # Injeção de DNA via I18N (O modelo fala tudo)
        self.px_hello = I18N.get("hello", {})
        self.px_prompt = I18N.get("language_prompt", {}) 
        self.px_arrow = I18N.get("arrow_instructions", {}) 
        self.px_labels = I18N.get("language_choices_labels", [])
        self.px_codes = I18N.get("language_choices_codes", [])

    def px_locate(self) -> str:
        """GPS do Pytrix: Refinaria, Raiz ou Bunker."""
        path = os.path.dirname(os.path.abspath(__file__))
        if "pytrix_models" in path:
            return "REFINARIA"
        elif os.path.exists("./pytrix.py") or os.path.exists("./.backup"):
            return "ROOT_SOVEREIGN"
        return "UNKNOWN_CONTEXT"

    def set_lang(self, choice: str) -> str:
        mapping = dict(zip(self.px_labels, self.px_codes))
        self.px_lang = mapping.get(choice, "pt")
        return self.px_lang

    def get_intro(self) -> Union[str, List[str]]:
        return self.px_hello.get(self.px_lang, list(self.px_hello.values()))

    def get_prompt(self) -> Union[str, List[str]]:
        return self.px_prompt.get(self.px_lang, list(self.px_prompt.values()))

    def get_arrow(self) -> Union[str, List[str]]:
        return self.px_arrow.get(self.px_lang, list(self.px_arrow.values()))

    def get_languages(self) -> List[str]:
        return self.px_labels

    def get_localized_text(self, key: str) -> str:
        return I18N.get(key, {}).get(self.px_lang, "")