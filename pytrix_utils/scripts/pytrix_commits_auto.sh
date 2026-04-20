#!/bin/bash

# Pytrix Forge - Git Auto-Sync Pro
# Local: Jacareí, SP - Refinaria de Código

echo "🚀 Pytrix: Iniciando sincronização via Shell..."

# 1. Definir pastas para ignorar (Regex para o grep)
IGNORE_PATTERN="venv/|pytrix_venv/|\.git/|__pycache__/|\.egg-info/"

# 2. Localizar arquivos novos ou modificados que não estão no ignore
# Usamos find por ser nativo e extremamente rápido no Debian
files=$(find . -maxdepth 2 -not -path '*/.*' -type f | grep -vE "$IGNORE_PATTERN")

count=0
summary=""

for file in $files; do
    # Pega apenas os primeiros 50 caracteres para o log, removendo quebras de linha
    content=$(head -c 50 "$file" | tr -d '\n\r')
    
    echo "  -> Adicionando: $file"
    git add "$file"
    
    # Acumula para o commit final
    summary+="${file##*/}: ${content}...\n"
    ((count++))
done

if [ $count -gt 0 ]; then
    git add -A
    # Commit único com todas as alterações (Batch processing)
    echo -e "feat(core): bulk sync $count files\n\n$summary" | git commit -F -
    echo "✅ Sucesso! $count arquivos processados na Refinaria."
else
    echo "Pytrix: Nada novo para sincronizar."
fi