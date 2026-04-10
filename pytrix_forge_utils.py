#!/bin/bash

# --- CONFIGURAÇÕES ---
APP_NAME=$1
TARGET_DIR="pytrix_utils/$APP_NAME"

if [ -z "$APP_NAME" ]; then
    echo "ERRO: Cadê o nome do app? Ex: ./pytrix_forge_utils.sh gerador_pdf"
    exit 1
fi

echo "🏗️  FORJANDO: $APP_NAME"

# 1. O TRANSPLANTE (Copia tudo para garantir que nada falte no início)
mkdir -p "$TARGET_DIR"
cp -r pytrix_models pytrix_views pytrix_i18n pytrix_controllers "$TARGET_DIR/"
cp pytrix.py "$TARGET_DIR/${APP_NAME}.py"

# 2. O SCANNER DE DNA (Sua lógica de 10 anos de aula)
# Pega os imports, transforma em caminho de arquivo e guarda num arquivo temporário
TEMP_LIST=$(mktemp)
grep -E "^(from|import) pytrix_" "$TARGET_DIR/${APP_NAME}.py" | while read -r linha; do
    modulo=$(echo "$linha" | awk '{print $2}')
    # Converte 'pytrix_models.vendas' em 'pytrix_models/vendas.py'
    echo "$modulo" | tr '.' '/' | sed 's/$/.py/' >> "$TEMP_LIST"
done

echo "🔍 Mapeando dependências reais..."

# 3. O EXTERMÍNIO (O que não está no 'ponto relativo' vira fumaça)
# Varremos todas as pastas pytrix_ dentro do novo app
find "$TARGET_DIR" -type f -name "*.py" | while read -r arquivo; do
    nome_base=$(basename "$arquivo")
    
    # Protege o arquivo principal e os dunder init
    if [[ "$nome_base" == "${APP_NAME}.py" || "$nome_base" == "__init__.py" ]]; then
        continue
    fi

    # Limpa o caminho para comparar (ex: utils/app/pytrix_models/vendas.py -> pytrix_models/vendas.py)
    path_limpo=$(echo "$arquivo" | sed "s|$TARGET_DIR/||")

    # Se NÃO estiver na lista de quem o app importa, tchau!
    if ! grep -q "$path_limpo" "$TEMP_LIST"; then
        rm "$arquivo"
        echo "  [🗑️] Removido: $path_limpo"
    fi
done

# 4. LIMPEZA DE PASTAS VAZIAS (Pra não ficar diretório fantasma)
find "$TARGET_DIR" -type d -empty -delete

# 5. O AJUSTE RELATIVO (O segredo da portabilidade)
sed -i "s/from pytrix_/from .pytrix_/g" "$TARGET_DIR/${APP_NAME}.py"

rm "$TEMP_LIST"
echo "✅ $APP_NAME está pronto e limpo na pasta utils/!"
