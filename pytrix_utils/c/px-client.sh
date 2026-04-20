#!/bin/bash
# px-client: O "Abridor" inteligente
FILE_PATH=$(realpath "$1")
SOCKET="/tmp/px-code.sock"

if [ -S "$SOCKET" ]; then
    # Se o editor j est no ar, envia o arquivo para uma nova aba
    echo "OPEN $FILE_PATH" | nc -U "$SOCKET"
    # Foca na janela do tmux onde o px-code est rodando
    tmux select-pane -t :.1 
else
    # Se no houver editor, inicia a sesso completa
    px-code "$FILE_PATH"
fi