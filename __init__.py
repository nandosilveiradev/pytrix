[project]
name = "pytrix"
version = "0.1.0"
description = "Ecossistema Pytrix"

[project.scripts]
pytrix = "pytrix:main"

[tool.setuptools]
# Adicione todos os seus pacotes core aqui para garantir que o 
# venv mapeie tudo corretamente no modo editável (-e .)
packages = [
    "pytrix_utils", 
    "pytrix_models", 
    "pytrix_controllers", 
    "pytrix_views", 
    "pytrix_i18n"
]