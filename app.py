# app.py

from controllers.controllers_select_language import ControllersSelectLanguage
#from controllers.controllers_mode_server import ControllersModeServer

class App:
    def __init__(self):
        self.select_language: ControllersSelectLanguage = ControllersSelectLanguage()

    def run(self):
        # roda seleção de idioma
        choice = self.select_language.run()   # retorna label escolhido, ex: "Português"
        print(self.select_language.lang)
        # agora passa o código para o ControllersModeServer
        #self.mode_server: ControllersModeServer = ControllersModeServer(self.select_language.lang)
        #self.mode_server.run()
        #self.options_ask1 = self.messages["ask_create_name_db"][self.lang]
        #self.options_ask2 = []
        
        #self.objetos: list[str] = self.messages["mode_options_labels"][self.lang].split("\n")
        
    
        def my_get_arrow(self,lang):
            self.lang = lang
            return I18N["arrow_instructions"][self.lang]

        return

if __name__ == "__main__":
    app = App()
    app.run()

import sys
from utils.tmux_controller import ensure_tmux_installed, start_or_attach_session
from utils.i18n_watcher import start_watcher
from controllers.controllers_select_language import ControllersSelectLanguage


class App:
    def __init__(self):
        self.select_language: ControllersSelectLanguage = ControllersSelectLanguage()

    def run(self):
        choice = self.select_language.run()
        print(self.select_language.lang)


if __name__ == "__main__":
    if "--inside-tmux" not in sys.argv:
        ensure_tmux_installed()
        start_or_attach_session()
    else:
        # inicia watcher em background
        start_watcher()

        app = App()
        app.run()