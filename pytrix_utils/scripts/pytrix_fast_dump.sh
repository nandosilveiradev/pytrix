#!/bin/bash

# Define o arquivo de saída
OUTPUT="sistema_pytrix_dump.txt"

echo "Gerando dump do código fonte (ignoring junk)..."

# Limpa o arquivo se já existir
> "$OUTPUT"

# Busca arquivos .py e .sh ignorando pastas de lixo
find . -type f \( -name "*.py" -o -name "*.sh" \) \
    -not -path "*/.*" \
    -not -path "*/venv/*" \
    -not -path "*/pytrix_venv/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/node_modules/*" \
    -exec sh -c '
        for file; do
            echo "========================================" >> "'$OUTPUT'"
            echo "FILE: $file" >> "'$OUTPUT'"
            echo "========================================" >> "'$OUTPUT'"
            # sed remove linhas em branco repetidas para encurtar o texto
            sed "/^$/d" "$file" >> "'$OUTPUT'"
            echo -e "\n" >> "'$OUTPUT'"
        done
    ' sh {} +

echo "Pronto! O código limpo está em: $OUTPUT"
echo "Dica: Use 'cat $OUTPUT | xclip -sel clip' para copiar tudo de uma vez."
