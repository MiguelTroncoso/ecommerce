#!/usr/bin/env bash
# Despliegue de ClickAndGo en el VPS de SuperFlash (inacap.superflash.site).
#
# Uso (desde el VPS, con sudo disponible):
#   sudo bash deploy/deploy_vps.sh
#
# El script es idempotente: puede ejecutarse varias veces.

set -Eeuo pipefail

REPO_URL="${REPO_URL:-https://github.com/MiguelTroncoso/ecommerce.git}"
BASE="${BASE:-/opt/clickandgo}"
APP="$BASE/app"
VENV="$BASE/venv"
DOMINIO="${DOMINIO:-inacap.superflash.site}"

echo "==> 1. Preparando carpetas en $BASE"
install -d -o www-data -g www-data "$BASE/sesiones" "$BASE/datos"
install -d "$BASE"

echo "==> 2. Obteniendo el codigo desde $REPO_URL"
if [ -d "$APP/.git" ]; then
    git -C "$APP" fetch --all --prune
    git -C "$APP" checkout main
    git -C "$APP" pull --ff-only origin main
else
    git clone "$REPO_URL" "$APP"
fi

echo "==> 3. Creando el entorno virtual e instalando dependencias"
if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r "$APP/web/requirements.txt"

echo "==> 4. Instalando el servicio systemd"
install -m 644 "$APP/deploy/clickandgo-web.service" /etc/systemd/system/clickandgo-web.service
systemctl daemon-reload
systemctl enable --now clickandgo-web.service
systemctl restart clickandgo-web.service

echo "==> 5. Publicando el sitio en Nginx"
install -m 644 "$APP/deploy/nginx-$DOMINIO.conf" "/etc/nginx/sites-available/$DOMINIO.conf"
ln -sf "/etc/nginx/sites-available/$DOMINIO.conf" "/etc/nginx/sites-enabled/$DOMINIO.conf"
nginx -t
systemctl reload nginx

echo "==> 6. Emitiendo/renovando el certificado TLS"
if [ -d "/etc/letsencrypt/live/$DOMINIO" ]; then
    certbot renew --quiet
else
    certbot --nginx -d "$DOMINIO" --non-interactive --agree-tos \
        --register-unsafely-without-email --redirect
fi
nginx -t
systemctl reload nginx

echo "==> 7. Verificacion"
sleep 2
curl -fsS -o /dev/null -w "local  : %{http_code}\n" http://127.0.0.1:3030/salud
curl -fsS -o /dev/null -w "publico: %{http_code}\n" "https://$DOMINIO/salud"
curl -fsS "https://$DOMINIO/salud" || true
echo
echo "Despliegue completado: https://$DOMINIO"
