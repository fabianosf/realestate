#!/usr/bin/env bash
# Uso: ./deploy_setup.sh <dominio> <postgres_password>
# Exemplo: ./deploy_setup.sh meusite.com Xk9#pLq2mZ!vR7

set -euo pipefail

DOMAIN="${1:-}"
PG_PASSWORD="${2:-}"
ENV_FILE="$(dirname "$0")/.env"
CERTS_DIR="$(dirname "$0")/nginx/certs"

# ── Validação de argumentos ────────────────────────────────────────────────────
if [[ -z "$DOMAIN" || -z "$PG_PASSWORD" ]]; then
  echo "Uso: $0 <dominio> <postgres_password>"
  echo "Ex : $0 meusite.com 'Xk9#pLq2mZ!vR7'"
  exit 1
fi

if [[ ${#PG_PASSWORD} -lt 16 ]]; then
  echo "ERRO: postgres_password deve ter pelo menos 16 caracteres."
  exit 1
fi

# ── Passo 1: Gerar SECRET_KEY ──────────────────────────────────────────────────
echo "→ Gerando SECRET_KEY..."
SECRET_KEY=$(python3 -c "
import secrets, string
chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'
print(''.join(secrets.choice(chars) for _ in range(64)))
")
echo "  SECRET_KEY gerada (64 chars)."

# ── Passo 2: Atualizar .env ────────────────────────────────────────────────────
echo "→ Atualizando .env..."

# Faz backup do .env atual
cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"

update_env() {
  local key="$1"
  local value="$2"
  # Escapa barras e caracteres especiais para sed
  local escaped_value
  escaped_value=$(printf '%s\n' "$value" | sed 's/[[\.*^$()+?{|]/\\&/g')
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${escaped_value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

update_env "SECRET_KEY"              "$SECRET_KEY"
update_env "DEBUG"                   "False"
update_env "POSTGRES_PASSWORD"       "$PG_PASSWORD"
update_env "ALLOWED_HOSTS"           "${DOMAIN},www.${DOMAIN}"
update_env "CORS_ALLOWED_ORIGINS"    "https://${DOMAIN},https://www.${DOMAIN}"
update_env "CSRF_TRUSTED_ORIGINS"    "https://${DOMAIN},https://www.${DOMAIN}"
update_env "REACT_APP_API_URL"       "https://${DOMAIN}/api"
update_env "DJANGO_SETTINGS_MODULE"  "config.settings.production"

echo "  .env atualizado com sucesso."

# ── Passo 3: Obter certificado SSL via Certbot ─────────────────────────────────
echo "→ Verificando Certbot..."
if ! command -v certbot &>/dev/null; then
  echo "  Certbot não encontrado. Instalando..."
  if command -v apt-get &>/dev/null; then
    apt-get update -qq && apt-get install -y -qq certbot
  elif command -v yum &>/dev/null; then
    yum install -y certbot
  else
    echo "ERRO: gerenciador de pacotes não suportado. Instale o certbot manualmente."
    exit 1
  fi
fi

echo "→ Solicitando certificado para ${DOMAIN} e www.${DOMAIN}..."
echo "  (certbot usará porta 80 — certifique-se de que Nginx está parado)"

# Para containers que usam porta 80, para o nginx antes do certbot
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q nginx; then
  echo "  Parando Nginx temporariamente..."
  docker stop "$(docker ps --format '{{.Names}}' | grep nginx)" 2>/dev/null || true
  NGINX_STOPPED=true
else
  NGINX_STOPPED=false
fi

certbot certonly \
  --standalone \
  --non-interactive \
  --agree-tos \
  --register-unsafely-without-email \
  -d "${DOMAIN}" \
  -d "www.${DOMAIN}"

# Retoma Nginx se foi parado
if [[ "$NGINX_STOPPED" == "true" ]]; then
  docker start "$(docker ps -a --format '{{.Names}}' | grep nginx)" 2>/dev/null || true
fi

# ── Copia certificados para nginx/certs ───────────────────────────────────────
echo "→ Copiando certificados para ${CERTS_DIR}..."
mkdir -p "$CERTS_DIR"

CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"

if [[ ! -f "${CERT_PATH}/fullchain.pem" ]]; then
  echo "ERRO: certificado não encontrado em ${CERT_PATH}"
  exit 1
fi

cp "${CERT_PATH}/fullchain.pem" "${CERTS_DIR}/fullchain.pem"
cp "${CERT_PATH}/privkey.pem"   "${CERTS_DIR}/privkey.pem"
chmod 600 "${CERTS_DIR}/privkey.pem"
chmod 644 "${CERTS_DIR}/fullchain.pem"

echo "  Certificados copiados com sucesso."

# ── Renovação automática (cron) ────────────────────────────────────────────────
echo "→ Configurando renovação automática do certificado..."
RENEW_SCRIPT="/etc/cron.d/certbot-rem"
cat > "$RENEW_SCRIPT" << CRON
0 3 * * * root certbot renew --quiet --post-hook "cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${CERTS_DIR}/fullchain.pem && cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${CERTS_DIR}/privkey.pem && docker restart \$(docker ps --format '{{.Names}}' | grep nginx) 2>/dev/null || true"
CRON
echo "  Renovação automática configurada (cron às 03:00 diariamente)."

# ── Sumário ────────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════"
echo "  Setup concluído com sucesso!"
echo "════════════════════════════════════════════"
echo "  Domínio   : ${DOMAIN}"
echo "  DEBUG     : False"
echo "  SSL       : ${CERTS_DIR}/"
echo "  Próximo   : docker compose -f docker-compose.prod.yml up -d --build"
echo "════════════════════════════════════════════"
