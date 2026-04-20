#!/bin/bash
# Script para reorganizar o MVP bagunçado em estrutura Pytrix
# Fernando - Pytrix Pipeline

# Criar pastas alvo com prefixo pytrix_
mkdir -p pytrix_core pytrix_controllers pytrix_views pytrix_models pytrix_utils pytrix_docs pytrix_tests pytrix_protocol
mkdir -p pytrix_utils/data pytrix_utils/docker pytrix_utils/scripts

# Núcleo da aplicação
mv app.py pytrix_core/ 2>/dev/null
mv pytrix.py pytrix_core/ 2>/dev/null
mv pytrix_core.py pytrix_core/ 2>/dev/null
mv pytrix_prefab_class.py pytrix_core/ 2>/dev/null

# Controladores (C + pipeline)
mv bip.c pytrix_controllers/ 2>/dev/null
mv pytrix_brain_watcher.c pytrix_controllers/ 2>/dev/null
mv pytrix_validator.py pytrix_controllers/ 2>/dev/null
mv validator.c pytrix_controllers/ 2>/dev/null
mv cleaner.c pytrix_controllers/ 2>/dev/null
mv pipeline.c pytrix_controllers/ 2>/dev/null

# Views
mv pytrix_views pytrix_views/ 2>/dev/null

# Models
mv pytrix_models pytrix_models/ 2>/dev/null

# Utils
mv pytrix_utils pytrix_utils/ 2>/dev/null
mv pytrix_docker pytrix_utils/docker/ 2>/dev/null
mv pytrix_docker_compose.yml pytrix_utils/docker/ 2>/dev/null
mv docker-compose.yml pytrix_utils/docker/ 2>/dev/null
mv Dockerfile pytrix_utils/docker/ 2>/dev/null
mv *.sh pytrix_utils/scripts/ 2>/dev/null

# Dados
mv data pytrix_utils/data/ 2>/dev/null
mv dados.xml pytrix_utils/data/ 2>/dev/null
mv sistema_pytrix_dump.txt pytrix_utils/data/ 2>/dev/null

# Documentação
mv docs pytrix_docs/ 2>/dev/null
mv README.md pytrix_docs/ 2>/dev/null
mv PYTRIX_README.md pytrix_docs/ 2>/dev/null
mv LICENSE pytrix_docs/ 2>/dev/null

# Testes
mv __pycache__ pytrix_tests/ 2>/dev/null

# Protocol (tudo que não se encaixa)
for f in *; do
  case "$f" in
    pytrix_core|pytrix_controllers|pytrix_views|pytrix_models|pytrix_utils|pytrix_docs|pytrix_tests|pytrix_protocol) ;;
    pyproject.toml|requirements.txt) ;;
    *)
      mv "$f" pytrix_protocol/ 2>/dev/null
      ;;
  esac
done

echo "Reorganização concluída. Revise a pasta 'pytrix_protocol/' para arquivos não classificados."
