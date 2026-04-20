#!/bin/bash

echo "--- [ AUDITORIA DE EMERGÊNCIA PYTRIX ] ---"
echo ""

# 1. Verifica a pasta de protocolos (o que você pediu)
echo ">> Conteúdo em pytrix_protocol:"
if [ -d "../../pytrix_protocol" ]; then
    ls -R ../../pytrix_protocol
else
    echo "ALERTA: Pasta pytrix_protocol não encontrada!"
fi

echo -e "\n>> Conteúdo em pytrix_core:"
ls -R ../../pytrix_core 2>/dev/null || echo "Vazia ou inexistente"

echo -e "\n>> Localização do Cérebro (Brain Watcher):"
find ../.. -name "pytrix_brain_watcher.c"

echo ""
echo "----------------------------------------"
echo "O Git está mostrando 'deleted' porque os arquivos saíram da RAIZ."
echo "Se os arquivos aparecerem na lista acima, eles ESTÃO SEGUROS."
