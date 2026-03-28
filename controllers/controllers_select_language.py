from models.model_select_language import ModelSelectLanguage
from views.view_select_language import ViewSelectLanguage


class ControllersSelectLanguage:
    def __init__(self):
        print("ControllersSelectLanguage Carregado")
        self.model: ModelSelectLanguage = ModelSelectLanguage()
        print("model_select Carregado")
        self.view: ViewSelectLanguage = ViewSelectLanguage()
        self.getlang: str 
        self.lang : str 
    
    def run(self):
        # imprime bloco
        self.view.show_value(self.model.bloco)

        # imprime hello (lista)
        for msg in self.model.get_intro():
            self.view.show_value(msg)

        # imprime prompt (lista)
        for msg in self.model.get_prompt():
            self.view.show_value(msg)

        # exibe menu de idiomas
        self.getlang = self.view.show_menu(
            self.model.get_languages(),
            " | ".join(self.model.get_arrow())  
        )


        self.lang = self.model.set_lang(self.getlang)

        #agora imprime só no idioma selecionado
        #self.view.show_value(self.model.get_intro())
        #self.view.show_value(self.model.get_prompt())
        #self.view.show_value(self.model.get_arrow())

        return self.lang