"""
app.py (legacy) : 
pytrix.py 
Enquanto instancia nativa pytrix.py, ao rodar forge o nome do pytrix.py será modificado para nome do utilitário
fica a critério do usuário manter o nome após forge
"""

from pytrix_controllers.pytrix_controllers_select_language import PytrixControllerSelectLanguage

class App:
    def __init__(self):
        # controlador responsável pela seleção de idioma
        self.select_language: PytrixControllerSelectLanguage = PytrixControllerSelectLanguage()

    def run(self):
        # ensure_tmux_installed() 
       
        # if "--inside-tmux" in sys.argv:
        #     # já estamos dentro da sessão, não chamar start_or_attach_session
        #     pass
        # else:
        #     from utils.tmux import start_or_attach_session
        #     start_or_attach_session()
        #     sys.exit(0)  # encerra aqui, porque o attach já cuida de rodar

        # roda seleção de idioma e imprime o idioma escolhido
        print("Agora vem a escolha do idioma: log ")
        idioma: str = self.select_language.run()
        print(f"{idioma}")

        # exemplo de como acessar mensagens traduzidas do dicionário
        # print(I18N["arrow_instructions"][self.select_language.lang])

        # aqui entraria ControllersModeServer se ativado
        # self.mode_server: ControllersModeServer = ControllersModeServer(self.select_language.lang)
        # self.mode_server.run()

        return idioma


def main():
    # função usada como entrypoint global (via pyproject.toml)
    app = App()
    app.run()


if __name__ == "__main__":
    # instancia a aplicação principal
    app = App()
    app.run()
