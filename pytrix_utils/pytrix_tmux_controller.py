import os
import subprocess
import sys

SESSION_NAME = "PytrixTmuxEnv"

def ensure_tmux_installed():
    try:
        subprocess.run(["tmux", "-V"], check=True, capture_output=True)
    except Exception:
        print("tmux não encontrado. Instale com:")
        print("sudo apt-get update && sudo apt-get install -y tmux")
        sys.exit(1)

def start_or_attach_session():
    project_root = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_root, "..", ".config", "tmuxPythonMVC.conf")
    script_path = os.path.join(project_root, "..", "app.py")

    result = subprocess.run(["tmux", "has-session", "-t", SESSION_NAME], capture_output=True)

    if result.returncode != 0:
        subprocess.run([
            "tmux", "new-session", "-d", "-s", SESSION_NAME, "-n", "app",
            f"bash -c 'tmux source-file {config_path}; docker-compose up -d; exec python3 {script_path} --inside-tmux'"
        ], check=True)

        subprocess.run([
            "tmux", "new-window", "-t", f"{SESSION_NAME}:1", "-n", "logs",
            "bash -c 'tail -f logs/app.log || echo "Nenhum log disponível"'"
        ], check=True)

    subprocess.run(["tmux", "attach", "-t", SESSION_NAME], check=True)
