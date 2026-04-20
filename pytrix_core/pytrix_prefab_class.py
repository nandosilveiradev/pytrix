import os
import sys
from textwrap import dedent


# Usamos dedent para que você possa indentar o código aqui no editor
# mas ele remova os espaços extras na hora de gravar o arquivo.

def create_mvc_prefab(name):
    name_lower = name.lower()
    name_camel = name.capitalize()

    # Configuração de caminhos baseada no seu 'tree'
    folders = ['models', 'controllers', 'views']
    
    

    templates = {
        "models": dedent(f"""\
            from .pytrix_models.model_base import ModelBase

            class Model{name_camel}(ModelBase):
                def __init__(self):
                    super().__init__()
                    self.table = '{name_lower}s'
            """),

        "controllers": dedent(f"""\
            from .pytrix_controllers.controller_base import ControllerBase

            class Controller{name_camel}(ControllerBase):
                def __init__(self, model, view):
                    self.model = model
                    self.view = view
            """),

        "views": dedent(f"""\
            from .pytrix_views.view_base import ViewBase

            class View{name_camel}(ViewBase):
                super().__init__()
                
            """)
    }

    for folder in folders:
        prefix = "model_" if folder == "models" else "controllers_" if folder == "controllers" else "view_"
        filename = f"{folder}/{prefix}{name_lower}.py"
        
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(templates[folder])
            print(f"✅ Criado: {filename}")
        else:
            print(f"⚠️  Arquivo já existe: {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_mvc_prefab(sys.argv[1])
    else:
        print("Uso: python3 pyclass_prefab.py NomeDaClasse")
