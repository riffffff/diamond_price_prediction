#!/bin/bash
# Script to obtain SSL certificate using Certbot
# Run this script on your VPS after the initial deployment

set -e

# Check if domain is provided
if [ -z "$1" ]; then
    echo "Usage: ./setup-ssl.sh your-domain.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

echo "Setting up SSL certificate for $DOMAIN..."
echo "Email: $EMAIL"

# Create directories for certbot
mkdir -p deploy/certbot/www
mkdir -p deploy/certbot/conf

# Request certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo ""
echo "✓ SSL certificate obtained successfully!"
echo ""
echo "Next steps:"
echo "1. Edit deploy/nginx.conf and replace YOUR_DOMAIN.com with $DOMAIN"
echo "2. Uncomment the HTTPS server block in deploy/nginx.conf"
echo "3. Uncomment the HTTP to HTTPS redirect in deploy/nginx.conf"
echo "4. Restart nginx: docker compose -f docker-compose.prod.yml restart nginx"
echo ""
