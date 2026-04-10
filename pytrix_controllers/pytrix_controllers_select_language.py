# pytrix_controllers/pytrix_controller_select_language.py
from pytrix_models.pytrix_model_select_language import PytrixModelSelectLanguage
from pytrix_views.pytrix_view_select_language import PytrixViewSelectLanguage

class PytrixControllerSelectLanguage:
    """
    Controller de orquestração para seleção de idioma Pytrix.
    Usa o padrão de variáveis px_ para otimização de fluxo interno e LSP.
    
    Herda de: Prefab MVC Pytrix
    Integração:
        - self.px_model: PytrixModelSelectLanguage
        - self.px_view: PytrixViewSelectLanguage
        
    Retorno:
        - px_lang_iso: String do idioma selecionado (ex: 'pt')
    """
    def __init__(self):
        print("PytrixControllersSelectLanguage Carregado")
        
        # Instâncias com prefixo px_ para acesso ultra-rápido via autocomplete
        self.px_model: PytrixModelSelectLanguage = PytrixModelSelectLanguage()
        print("pytrix_model_select Carregado")
        
        self.px_view: PytrixViewSelectLanguage = PytrixViewSelectLanguage()
        
        # Atributos de estado interno protegidos
        self.px_lang_raw: str = ""
        self.px_lang_iso: str = ""

    def run(self) -> str:
        """
        Executa o fluxo visual de seleção. 
        Acesso direto aos atributos px_ do model economiza ciclos de busca.
        """
        # Exibe o identificador do bloco (referência direta na memória)
        self.px_view.show_value(self.px_model.px_bloco)

        # Itera sobre mensagens de boas-vindas
        for msg in self.px_model.get_intro():
            self.px_view.show_value(msg)

        # Itera sobre os prompts de orientação
        for msg in self.px_model.get_prompt():
            self.px_view.show_value(msg)

        # Dispara o menu CLI (Questionary)
        # O autocomplete do LSP vai sugerir px_labels e px_arrow instantaneamente
        self.px_lang_raw = self.px_view.show_menu(
            self.px_model.px_labels,
            " | ".join(self.px_model.px_arrow)
        )

        # Define o idioma no Model e captura o código final
        self.px_lang_iso = self.px_model.set_lang(self.px_lang_raw)

        return self.px_lang_iso