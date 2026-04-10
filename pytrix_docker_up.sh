#!/bin/bash

# Pytrix Docker Infrastructure Boot
# Script para subir o ambiente e validar permissões de rede

echo "🐳 Subindo ecossistema Pytrix via Docker..."

# 1. Garante permissão nos scripts de infraestrutura interna
if [ -f ".docker/dns/setup-dns.sh" ]; then
    echo "🔧 Validando permissões de execução no setup-dns..."
    chmod +x .docker/dns/setup-dns.sh
fi

# 2. Sobe os containers usando o arquivo específico do ecossistema
docker-compose -f pytrix_docker_compose.yml up -d

# 3. Exibe o status para conferência rápida no terminal
echo "📊 Status dos containers Pytrix:"
docker-compose -f pytrix_docker_compose.yml ps

echo "🚀 Infraestrutura Pytrix_Docker operacional!"
