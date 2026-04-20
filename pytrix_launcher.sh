#!/bin/bash
SESSION="pytrix"

# 1. Garante que começamos do zero
tmux kill-server 2>/dev/null
sleep 0.2

# 2. Inicia o servidor tmux explicitamente antes de criar sessões
tmux start-server

# 3. Cria a sessão. 
# USAMOS 'bash' como comando principal e chamamos o px-code depois.
# Assim, se o px-code crashar, a janela do tmux NÃO FECHA.
tmux new-session -d -s $SESSION -n "Editor" "bash"

sleep 0.3

# 4. Envia o comando para o editor dentro da janela já aberta
tmux send-keys -t $SESSION:0 "/bin/px-code $1" C-m

# 5. Tenta o split para a IA
tmux split-window -h -t $SESSION "python3 /root/pytrix/pytrix_ai_watcher.py || bash"

# 6. Anexa
tmux attach-session -t $SESSION