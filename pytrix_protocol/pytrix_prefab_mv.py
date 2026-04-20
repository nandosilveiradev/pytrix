import os
import sys

def pytrix_prefab_mvc(name):
    name_lower = name.lower()
    name_camel = name.capitalize()

    # Pastas seguindo a estrutura real do seu projeto
    folders = ['pytrix_models', 'pytrix_controllers', 'pytrix_views']
    
    templates = {
        "pytrix_models": f"""from pytrix_models.pytrix_model_base import PytrixModelBase

class PytrixModel{name_camel}(PytrixModelBase):
    \"\"\"
    Modelo especializado para {name_camel}.
    Usa o padrão px_ para indexação via LSP.
    \"\"\"
    def __init__(self):
        super().__init__()
        self.px_name: str = "PytrixModel{name_camel}"
        
        # Importação local do I18N para manter a performance
        from pytrix_i18n.i18n import I18N
        self.px_bloco: str = I18N.get("{name_lower}_block", "Pytrix_Default_Block")""",
        
        "pytrix_controllers": f"""from pytrix_models.pytrix_model_{name_lower} import PytrixModel{name_camel}
from pytrix_views.pytrix_view_{name_lower} import PytrixView{name_camel}

class PytrixController{name_camel}:
    \"\"\"
    Controller de orquestração para {name_camel}.
    Instâncias px_ para acesso ultra-rápido via autocomplete.
    \"\"\"
    def __init__(self):
        self.px_model: PytrixModel{name_camel} = PytrixModel{name_camel}()
        self.px_view: PytrixView{name_camel} = PytrixView{name_camel}()

    def run(self) -> bool:
        # Segue a filosofia do SelectLanguage
        self.px_view.show_value(self.px_model.px_bloco)
        return True""",
        
        "pytrix_views": f"""from pytrix_views.pytrix_view_base import PytrixViewBase

class PytrixView{name_camel}(PytrixViewBase):
    \"\"\"
    Interface para {name_camel}.
    Herda de: PytrixViewBase
    \"\"\"
    def __init__(self):
        super().__init__()
        self.px_name: str = "PytrixView{name_camel}" """
    }

    for folder in folders:
        # Ajuste dos prefixos de arquivo conforme o seu padrão
        if "models" in folder:
            prefix = "pytrix_model_"
        elif "controllers" in folder:
            prefix = "pytrix_controller_"
        else:
            prefix = "pytrix_view_"
            
        filename = f"{folder}/{prefix}{name_lower}.py"
        
        if not os.path.exists(filename):
            # Garante que a pasta existe antes de criar o arquivo
            os.makedirs(folder, exist_ok=True)
            with open(filename, "w") as f:
                f.write(templates[folder])
            print(f"✅ Forjado: {filename}")
        else:
            print(f"⚠️  Soberania mantida: {filename} já existe.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pytrix_prefab_mvc(sys.argv[1])
    else:
        print("Uso: python3 pytrix_prefab.py NomeDoMódulo")