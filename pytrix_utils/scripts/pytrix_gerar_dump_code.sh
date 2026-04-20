find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.yml" -o -name "*.md" \) \
    -not -path "*/pytrix_venv/*" \
    -not -path "*/venv/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/data/*" \
    -not -path "*/docs/*" \
    -not -path "*/web/*" \
    -not -path "*/letsencrypt/*" \
    -name "pytrix_*" \
    -exec sh -c '
        for file; do
            echo "========================================"
            echo "FILE: $file"
            echo "========================================"
            cat "$file"
            echo -e "\n"
        done
    ' sh {} + > pytrix_dump.txt

echo "✅ dump gerado em pytrix_dump.txt"