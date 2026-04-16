#!/bin/bash
# Puxa suas configs do Git e linka no root
REPO_PATH="/root/seus-dotfiles/sublime-user"
TARGET_PATH="/root/.config/sublime-text/Packages/User"

rm -rf "$TARGET_PATH"
ln -s "$REPO_PATH" "$TARGET_PATH"

echo "💎 Sublime Text agora está com a sua cara!"