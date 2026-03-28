import os
import sys

def create_mvc_prefab(name):
    name_lower = name.lower()
    name_camel = name.capitalize()

    # Configuração de caminhos baseada no seu 'tree'
    folders = ['models', 'controllers', 'views']
    
    templates = {
        "models": f"""from models.model_base import ModelBase\n\nclass Model{name_camel}(ModelBase):\n    def __init__(self):\n        super().__init__()\n        self.table = '{name_lower}s'""",
        
        "controllers": f"""from controllers.__init__ import *\n\nclass Controller{name_camel}:\n    def __init__(self, model, view):\n        self.model = model\n        self.view = view""",
        
        "views": f"""from views.view_base import ViewBase\n\nclass View{name_camel}(ViewBase):\n    def render(self):\n        # Aqui entra o Grid de 12 colunas\n        return self.render_container(self.render_col(12, "<h1>{name_camel}</h1>"))"""
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
