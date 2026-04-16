#!/bin/bash
echo "🐳 Subindo ecossistema Pytrix via Docker..."

# 1. Permissão no scriptdns
if [ -f "pytrix_docker/dns/scriptdns.sh" ]; then
    echo "🔧 Validando permissões no scriptdns..."
    chmod +x pytrix_docker/dns/scriptdns.sh
fi

# 2. Sobe os containers com as variáveis carregadas no shell
echo "🚀 Carregando variáveis e subindo containers..."

# O comando 'export' garante que o Docker Compose veja as variáveis do arquivo
export $(grep -v '^#' .pytrix_env | xargs)

docker compose -f pytrix_docker_compose.yml up -d

# 2. Primeira tentativa de subir
docker compose -f pytrix_docker_compose.yml --env-file .pytrix_env up -d

# 3. Status inicial
echo "📊 Status atual:"
docker compose -f pytrix_docker_compose.yml ps

# 4. Aguarda negociação
echo "⏳ Validando conexão com Cloudflare..."
sleep 5

# 5. Check de conexão e tentativa de ressubir se falhar
if docker logs pytrix_tunnel 2>&1 | grep -q "Connected to GRU"; then
    echo "🚀 Pytrix conectado ao Edge (GRU)!"
    echo "🔗 https://pytrix.eu.org"
else
    echo "⚠️ Conexão não detectada. Tentando ressubir com env-file forçado..."
    
    # Para e sobe de novo garantindo o env-file
    docker compose -f pytrix_docker_compose.yml --env-file .pytrix_env down
    docker compose -f pytrix_docker_compose.yml --env-file .pytrix_env up -d
    
    echo "🔄 Comando de reinicialização enviado. Verifique os logs em instantes."
fi