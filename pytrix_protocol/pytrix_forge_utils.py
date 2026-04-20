#!/bin/bash

# --- CONFIGURAÇÕES SOBERANAS ---
ADMIN_NAME="Fernando Silveira"
ADMIN_EMAIL="fernandosilveiradev@gmail.com"
OFFICIAL_REMOTE="github.com/nandosilveira/pytrix"

APP_NAME=$1
TARGET_DIR="pytrix_utils/$APP_NAME"
FORGE_BRANCH="forge/${APP_NAME}_$(date +%s)" # ID único para a branch de build

if [ -z "$APP_NAME" ]; then
    echo "❌ ERRO: ./pytrix_forge.sh nome_do_app"
    exit 1
fi

# --- 0. A RAIZ DA FORJA (Criação do ambiente isolado) ---
git checkout main
git pull origin main
git checkout -b "$FORGE_BRANCH"

echo "🏗️  FORJANDO EM BRANCH ISOLADA: $FORGE_BRANCH"

# --- 1. TRAVA DE SOBERANIA ---
if [[ $(git config user.name) != "$ADMIN_NAME" ]]; then
    git config --local user.name "$ADMIN_NAME"
    git config --local user.email "$ADMIN_EMAIL"
fi

# --- 2. O TRANSPLANTE & 3. O LOG DE NASCIMENTO ---
mkdir -p "$TARGET_DIR"
mv pytrix_models pytrix_views pytrix_i18n pytrix_controllers "$TARGET_DIR/"
mv pytrix.py "$TARGET_DIR/${APP_NAME}.py"

LOG_FILE="$TARGET_DIR/pytrix_forge.log"
{
    echo "APP: $APP_NAME"
    echo "DATA/HORA: $(date '+%d/%m/%Y %H:%M:%S')"
    echo "BRANCH DE ORIGEM: $FORGE_BRANCH"
    echo "FORJADOR: $(git config user.name)"
} > "$LOG_FILE"

# --- 4. SCANNER DE DNA & 5. O EXTERMÍNIO ---
TEMP_LIST=$(mktemp)
grep -E "^(from|import) pytrix_" "$TARGET_DIR/${APP_NAME}.py" | while read -r linha; do
    modulo=$(echo "$linha" | awk '{print $2}')
    echo "$modulo" | tr '.' '/' | sed 's/$/.py/' >> "$TEMP_LIST"
done

find "$TARGET_DIR" -type f -name "*.py" | while read -r arquivo; do
    nome_base=$(basename "$arquivo")
    if [[ "$nome_base" == "${APP_NAME}.py" || "$nome_base" == "__init__.py" || "$nome_base" == "pytrix_forge.log" ]]; then
        continue
    fi
    path_limpo=$(echo "$arquivo" | sed "s|$TARGET_DIR/||")
    if ! grep -q "$path_limpo" "$TEMP_LIST"; then
        rm "$arquivo"
    fi
done

# --- 6. FINALIZAÇÃO ---
find "$TARGET_DIR" -type d -empty -delete
sed -i "s/from pytrix_/from .pytrix_/g" "$TARGET_DIR/${APP_NAME}.py"
rm "$TEMP_LIST"

# --- 7. O PUSH DA BRANCH DE FORJA ---
git add "$TARGET_DIR"
git commit -m "forge: $APP_NAME ($ADMIN_NAME)"
git push origin "$FORGE_BRANCH"

echo "✅ Forja concluída na branch $FORGE_BRANCH"
echo "💡 Agora você pode fazer o Merge ou fechar o PR para a Main."












