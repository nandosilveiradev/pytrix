#!/bin/bash
# /usr/local/bin/python-pytrix

SCRIPT_PATH=$(readlink -f "$1")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
SCRIPT_NAME=$(basename "$SCRIPT_PATH")
BIN_PATH="${SCRIPT_DIR}/${SCRIPT_NAME%.py}.bin"

# 1. Gera o Hash do arquivo atual
CURRENT_HASH=$(xxhsum "$SCRIPT_PATH" | awk '{print $1}')

# 2. Verifica se o binário existe e se o Hash bate
if [ -f "$BIN_PATH" ]; then
    STORED_HASH=$(getfattr --only-values -n user.pytrix_hash "$BIN_PATH" 2>/dev/null)
    
    if [ "$CURRENT_HASH" == "$STORED_HASH" ]; then
        # SHORT-CIRCUIT: Executa o binário nativo direto
        exec "$BIN_PATH" "${@:2}"
    fi
fi

# 3. Se o Hash mudou ou não existe, executa via Python e agenda Cristalização
# O '&' garante que a compilação não trave a sua execução atual
(
    nuitka --quiet --remove-output --output-filename="$BIN_PATH" "$SCRIPT_PATH"
    setfattr -n user.pytrix_hash -v "$CURRENT_HASH" "$BIN_PATH"
    # Limpeza LRU: Remove binários não usados se o disco passar de 5GB de cache
    pytrix-cleaner --threshold 5G 
) &

exec /usr/bin/python3 "$@"