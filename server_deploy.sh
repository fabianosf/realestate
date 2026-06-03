#!/usr/bin/env bash
# Deploy completo em produção — captei.shop
# Uso: sudo bash server_deploy.sh <GITHUB_TOKEN> <POSTGRES_PASSWORD>
# Ex : sudo bash server_deploy.sh ghp_SEU_TOKEN_NOVO 'MinhaS3nh@Forte!2024'

set -euo pipefail

# ── Argumentos ─────────────────────────────────────────────────────────────────
GITHUB_TOKEN="${1:-}"
PG_PASSWORD="${2:-}"

if [[ -z "$GITHUB_TOKEN" || -z "$PG_PASSWORD" ]]; then
  echo "Uso: sudo bash $0 <GITHUB_TOKEN> <POSTGRES_PASSWORD>"
  exit 1
fi

if [[ ${#PG_PASSWORD} -lt 16 ]]; then
  echo "ERRO: POSTGRES_PASSWORD deve ter pelo menos 16 caracteres."
  exit 1
fi

# ── Variáveis fixas ────────────────────────────────────────────────────────────
DOMAIN="captei.shop"
SERVER_IP="92.113.33.16"
REPO_URL="https://${GITHUB_TOKEN}@github.com/fabianosf/realestate.git"
APP_DIR="/opt/real-estate-mining"
CERTS_DIR="${APP_DIR}/nginx/certs"

# ── 1. Dependências do sistema ─────────────────────────────────────────────────
echo "[1/7] Instalando dependências do sistema..."
apt-get update -qq
apt-get install -y -qq \
  git curl ca-certificates gnupg lsb-release certbot \
  2>/dev/null

# Docker
if ! command -v docker &>/dev/null; then
  echo "  → Instalando Docker..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
fi

# Docker Compose plugin
if ! docker compose version &>/dev/null 2>&1; then
  echo "  → Instalando Docker Compose plugin..."
  apt-get install -y -qq docker-compose-plugin
fi

echo "  ✓ Dependências OK."

# ── 2. Clone / pull do repositório ─────────────────────────────────────────────
echo "[2/7] Sincronizando repositório..."
if [[ -d "${APP_DIR}/.git" ]]; then
  cd "$APP_DIR"
  # Atualiza o remote com o novo token sem expor no log
  git remote set-url origin "$REPO_URL"
  git pull origin main --rebase
  echo "  ✓ Repositório atualizado (pull)."
else
  git clone "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
  echo "  ✓ Repositório clonado."
fi

# Remove token da URL do remote após uso (segurança)
git remote set-url origin "https://github.com/fabianosf/realestate.git"

# ── 3. Gerar SECRET_KEY ────────────────────────────────────────────────────────
echo "[3/7] Gerando SECRET_KEY..."
SECRET_KEY=$(python3 -c "
import secrets, string
chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'
print(''.join(secrets.choice(chars) for _ in range(64)))
")
echo "  ✓ SECRET_KEY gerada."

# ── 4. Criar/atualizar .env de produção ────────────────────────────────────────
echo "[4/7] Criando .env de produção..."

cat > "${APP_DIR}/.env" << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},${SERVER_IP}
DJANGO_SETTINGS_MODULE=config.settings.production

POSTGRES_DB=realestate_mining
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${PG_PASSWORD}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0

CORS_ALLOWED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}

REACT_APP_API_URL=https://${DOMAIN}/api

PROXY_LIST=
EOF

chmod 600 "${APP_DIR}/.env"
echo "  ✓ .env criado (permissão 600)."

# ── 5. Certificado SSL via Certbot ─────────────────────────────────────────────
echo "[5/7] Obtendo certificado SSL para ${DOMAIN}..."
mkdir -p "$CERTS_DIR"

CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"

if [[ -f "${CERT_PATH}/fullchain.pem" ]]; then
  echo "  → Certificado já existe, renovando se necessário..."
  certbot renew --quiet
else
  echo "  → Emitindo novo certificado (porta 80 deve estar livre)..."

  # Para qualquer container usando porta 80
  docker ps --format '{{.Names}}' | grep -i nginx | xargs -r docker stop || true

  certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --register-unsafely-without-email \
    -d "${DOMAIN}" \
    -d "www.${DOMAIN}"
fi

cp "${CERT_PATH}/fullchain.pem" "${CERTS_DIR}/fullchain.pem"
cp "${CERT_PATH}/privkey.pem"   "${CERTS_DIR}/privkey.pem"
chmod 644 "${CERTS_DIR}/fullchain.pem"
chmod 600 "${CERTS_DIR}/privkey.pem"

# Cron de renovação automática (03:00 diário)
CRON_JOB="0 3 * * * root certbot renew --quiet --post-hook \"cp ${CERT_PATH}/fullchain.pem ${CERTS_DIR}/fullchain.pem && cp ${CERT_PATH}/privkey.pem ${CERTS_DIR}/privkey.pem && docker ps --format '{{.Names}}' | grep nginx | xargs -r docker restart\""
echo "$CRON_JOB" > /etc/cron.d/certbot-captei
echo "  ✓ SSL configurado + renovação automática."

# ── 6. Build e deploy com Docker Compose ───────────────────────────────────────
echo "[6/7] Executando build e deploy..."
cd "$APP_DIR"

# Para stack anterior se existir
docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

# Build e sobe todos os containers
docker compose -f docker-compose.prod.yml up --build -d

echo "  ✓ Containers iniciados."

# ── 7. Migrations e collectstatic ─────────────────────────────────────────────
echo "[7/7] Aguardando API ficar pronta e executando migrations..."

# Aguarda o container da API estar saudável (máx 120s)
WAIT=0
until docker compose -f docker-compose.prod.yml exec -T api python manage.py check --deploy 2>/dev/null; do
  sleep 5
  WAIT=$((WAIT + 5))
  if [[ $WAIT -ge 120 ]]; then
    echo "ERRO: API não ficou pronta em 120s."
    docker compose -f docker-compose.prod.yml logs api | tail -20
    exit 1
  fi
done

docker compose -f docker-compose.prod.yml exec -T api \
  python manage.py migrate --noinput

docker compose -f docker-compose.prod.yml exec -T api \
  python manage.py collectstatic --noinput --clear

docker compose -f docker-compose.prod.yml exec -T api \
  python manage.py seed_admin

echo "  ✓ Migrations, collectstatic e seed_admin executados."

# ── Sumário final ──────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  DEPLOY CONCLUÍDO COM SUCESSO"
echo "═══════════════════════════════════════════════════"
echo "  Dashboard : https://${DOMAIN}"
echo "  Admin     : https://${DOMAIN}/admin/"
echo "  API       : https://${DOMAIN}/api/"
echo "  Login     : fabiano.freitas@gmail.com / 260281xx"
echo "  AÇÃO      : Troque a senha após o primeiro acesso!"
echo "═══════════════════════════════════════════════════"
docker compose -f docker-compose.prod.yml ps
