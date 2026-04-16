#!/bin/bash

echo "🚀 Iniciando a Infraestrutura Pytrix..."

# 1. Limpeza preventiva (remove containers com nomes conflitantes)
docker rm -f pytrix_static pytrix_tunnel_quick pytrix_tunnel static-web-1 static-tunnel-1 2>/dev/null

# 2. Sobe o ambiente Static (Nginx + Tunnel)
echo "🌐 Subindo ambiente Static..."
docker compose -p static up -d

# 3. Sobe o ambiente Core (Framework Pytrix)
echo "⚙️ Subindo ambiente Core..."
docker compose -f pytrix_docker_compose.yml -p core up -d

# 4. Pequeno delay para a Cloudflare gerar o link
echo "⏳ Aguardando o túnel da Cloudflare..."
sleep 5

# 5. Extrai e exibe o link do túnel
TUNNEL_LINK=$(docker logs static-tunnel-1 2>&1 | grep -o "https://.*trycloudflare.com")

echo "-------------------------------------------------------"
echo "✅ TUDO ONLINE!"
echo "📍 Link Público: $TUNNEL_LINK"
echo "📍 Local: http://localhost:8080"
echo "-------------------------------------------------------"

# 6. Segue o log do container web para monitorar acessos
echo "📊 Monitorando acessos ao Nginx (Ctrl+C para sair do log)..."
docker logs -f static-web-1