#!/bin/bash
source .pytrix_env

# 0. LIMPEZA
./pytrix_clean.sh

# 1. ESCANEIA IMPORTS
TEMP_LIST=$(mktemp)
grep -rE "^(from|import) pytrix_" ./*.py | awk '{print $2}' | \
    tr '.' '/' | sed 's/$/.py/' >> "$TEMP_LIST"

# 2. CRUZA COM REQUIREMENTS — remove libs externas
if [ -f "requirements.txt" ]; then
    while read -r lib; do
        sed -i "/$lib/d" "$TEMP_LIST"
    done < requirements.txt
fi

# 3. PERGUNTA O NOME
read -p "nome do util: " APP_NAME
TARGET_DIR="pytrix_utils/pytrix_${APP_NAME}"
mkdir -p "$TARGET_DIR"

# 4. COLISÃO DE NOME
FORGE_LOG="pytrix_forge_audit.log"
if grep -q "forge\[pytrix_${APP_NAME}\]" "$FORGE_LOG" 2>/dev/null; then
    echo "⚠️  'pytrix_${APP_NAME}' já existe:"
    grep "forge\[pytrix_${APP_NAME}\]" "$FORGE_LOG"
    read -p "continuar mesmo assim? (s/n): " CONFIRM
    if [ "$CONFIRM" = "s" ]; then
        HASH=$(echo "$APP_NAME$PYTRIX_GIT_EMAIL$(date +%s)" | md5sum | cut -c1-6)
        APP_NAME="${APP_NAME}_${HASH}"
        TARGET_DIR="pytrix_utils/pytrix_${APP_NAME}"
        mkdir -p "$TARGET_DIR"
        echo "novo nome: pytrix_$APP_NAME"
    else
        exit 0
    fi
fi

echo "🏗️  FORJANDO: pytrix_$APP_NAME"

# 5. MOVE O QUE ESTÁ NA LISTA
while read -r arquivo; do
    [ -f "$arquivo" ] && mv "$arquivo" "$TARGET_DIR/"
done < "$TEMP_LIST"

# tenta raiz primeiro, depois utils
if [ -f "pytrix_${APP_NAME}.py" ]; then
    mv "pytrix_${APP_NAME}.py" "$TARGET_DIR/pytrix_${APP_NAME}.py"
elif [ -f "pytrix_utils/pytrix_${APP_NAME}.py" ]; then
    mv "pytrix_utils/pytrix_${APP_NAME}.py" "$TARGET_DIR/pytrix_${APP_NAME}.py"
else
    echo "❌ arquivo principal não encontrado"
    exit 1
fi

# 6. AJUSTE RELATIVO
sed -i "s/from pytrix_/from .pytrix_/g" "$TARGET_DIR/pytrix_${APP_NAME}.py"
rm "$TEMP_LIST"

# 7. AUDITORIA
git config user.email "$PYTRIX_GIT_EMAIL"
git config user.name  "$PYTRIX_GIT_NAME"
echo "forge[pytrix_${APP_NAME}]: $(date '+%Y-%m-%d %H:%M') | $PYTRIX_GIT_EMAIL" >> "$FORGE_LOG"

# 8. ENVIA SÓ O UTIL
git add "$TARGET_DIR" "$FORGE_LOG"
git commit -m "forja utils[pytrix_${APP_NAME}]"
git push origin main

# 9. RAIZ VOLTA DO REPO
git pull
git rebase origin/main

echo "✅ pytrix_${APP_NAME} forjado e raiz reconstituída!"