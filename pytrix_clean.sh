#!/bin/bash

# Pytrix Trash Collector
# Focado em limpar resíduos de refatoração e arquivos temporários

echo "🧹 Iniciando limpeza de tralha no ecossistema Pytrix..."

# 1. Removendo __pycache__ recursivamente (O comando que você pediu)
# Essencial para eliminar bytecodes de arquivos que mudaram de nome
find . -name "__pycache__" -type d -exec rm -rf {} +

# 2. Removendo resíduos de testes e build do pytest/tox
if [ -d ".pytest_cache" ]; then rm -rf .pytest_cache; fi
if [ -d ".tox" ]; then rm -rf .tox; fi

# 3. Removendo arquivos temporários de edição (se houver)
find . -name "*.tmp" -type f -delete
find . -name "*.bak" -type f -delete

# 4. Limpeza de metadados de builds anteriores da documentação
# (Opcional: limpa a pasta de docs antes de gerar uma nova)
if [ -d "pytrix_docs/pytrix" ]; then
    echo "📚 Limpando documentação antiga..."
    rm -rf pytrix_docs/pytrix
fi

echo "✨ Tudo limpo! Ambiente pronto para o novo push."

