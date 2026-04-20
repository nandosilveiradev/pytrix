#!/bin/bash
# Inicializa o ambiente Pytrix com nnn, px-code e Watcher

# 1. Gera o .env se no existir
if [ ! -f .env-px-code ]; then
    generate_default_env # Baseado na deteco de extenses local
fi

# 2. Cria a sesso tmux com o layout sugerido
tmux new-session -d -s "pytrix_$(basename $PWD)"

# Split da Esquerda (nnn)
tmux send-keys -t 0 'nnn' C-m

# Split Central (Editor)
tmux split-window -h -p 85
tmux send-keys -t 1 'px-code' C-m

# Split Inferior (Watcher/Sugestes)
tmux split-window -v -p 20 -t 1
tmux send-keys -t 2 'python3 watcher_pytrix.py' C-m

# Foca no editor
tmux select-pane -t 1
tmux attach-session -t "pytrix_$(basename $PWD)"
