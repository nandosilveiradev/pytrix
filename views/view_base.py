# views/view_base.py
# essa classe deve ser usada para servir de base para ser herdada para toda view que for gerada 
import questionary

class ViewBase:
    # CLI View for user interaction
    def __init__(self):
        self.stats = True

    def show_message(self, message: str):
        """Retorna uma mensagem genérica"""
        return message

    def show_error(self, error: str):
        """Retorna uma mensagem de erro"""
        return f"[ERRO] {error}"

    def show_success(self, success: str):
        """Retorna uma mensagem de sucesso"""
        return f"[OK] {success}"

    def show_menu(self, languages, prompt):
        choice = questionary.select(
            prompt,
            choices=languages
        ).ask()
        return choice

    def show_value(self,msg):
        # Esta deve ser a única linha que imprime algo aqui.
        print(f"{msg}") 
        # Certifique-se de
    

