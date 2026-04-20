#!/bin/bash

# Configurações vindas do .pytrix_env
DOMAIN=${LOCAL_DOMAIN:-pytrix.local}
EXT_IP=$(hostname -I | awk '{print $1}')
REVERSE_NET=$(echo $EXT_IP | awk -F. '{print $3"."$2"."$1}')
LAST_OCTET=$(echo $EXT_IP | awk -F. '{print $4}')

# 1. Configuração de Opções (Permite consultas e define forwarders dinâmicos)
cat <<EOF > /etc/bind/named.conf.options
options {
    directory "/var/cache/bind";
    recursion yes;
    allow-query { any; };
    forwarders {
        ${PRIMARY_DNS:-8.8.8.8};
        ${SECONDARY_DNS:-1.1.1.1};
    };
    dnssec-validation auto;
    listen-on-v6 { any; };
};
EOF

# 2. Configuração do named.conf.local
cat <<EOF > /etc/bind/named.conf.local
zone "$DOMAIN" { type master; file "/etc/bind/db.$DOMAIN"; };
zone "$REVERSE_NET.in-addr.arpa" { type master; file "/etc/bind/db.rev"; };
EOF

# 3. Zona Direta
cat <<EOF > /etc/bind/db.$DOMAIN
\$TTL 604800
@ IN SOA ns1.$DOMAIN. admin.$DOMAIN. ( $(date +%Y%m%d%H) 8H 2H 4W 1D )
@ IN NS ns1.$DOMAIN.
ns1 IN A $EXT_IP
@ IN A $EXT_IP
EOF

# 4. Subdomínios Dinâmicos
if [ ! -z "$SUBDOMAINS" ]; then
    IFS=',' read -ra SUBS <<< "$SUBDOMAINS"
    for sub in "${SUBS[@]}"; do
        if [ "$sub" != "@" ]; then
            echo "$sub IN A $EXT_IP" >> /etc/bind/db.$DOMAIN
        fi
    done
fi

# 5. Zona Reversa
cat <<EOF > /etc/bind/db.rev
\$TTL 604800
@ IN SOA ns1.$DOMAIN. admin.$DOMAIN. ( $(date +%Y%m%d%H) 8H 2H 4W 1D )
@ IN NS ns1.$DOMAIN.
$LAST_OCTET IN PTR $DOMAIN.
EOF

# 6. Início dos Serviços
chown -R bind:bind /etc/bind /var/cache/bind /var/lib/bind

# Inicia o SSH usando o caminho absoluto
/usr/sbin/sshd

echo "🌍 DNS rodando em $EXT_IP para o domínio $DOMAIN"

# Inicia o Bind e mantém o container vivo
exec named -g -u bind