#!/bin/bash

# =============================================================================
# Domain & SSL Setup Script for DigitalOcean
# =============================================================================
# This script helps configure domain and SSL certificates
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

print_header "🌐 VAIDYAVIHAR - DOMAIN & SSL SETUP"

# =============================================================================
# STEP 1: Domain Input
# =============================================================================
print_header "STEP 1: Domain Configuration"

read -p "Enter your domain name (e.g., vaidya-vihar.com): " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    print_error "Domain name is required!"
    exit 1
fi

print_info "Domain: $DOMAIN_NAME"

# Get current IP
CURRENT_IP=$(curl -s http://checkip.amazonaws.com)
print_info "Current server IP: $CURRENT_IP"

echo -e "\n${YELLOW}⚠️  IMPORTANT: Before continuing, make sure:${NC}"
echo "  1. Your domain's A record points to: $CURRENT_IP"
echo "  2. DNS has propagated (can take 5-30 minutes)"
echo "  3. You can access your site at: http://$DOMAIN_NAME"
echo ""

read -p "Has your domain DNS propagated? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Please wait for DNS propagation and run this script again."
    print_info "You can check DNS propagation at: https://dnschecker.org/"
    exit 0
fi

# Test domain resolution
DOMAIN_IP=$(dig +short $DOMAIN_NAME | head -1)
if [ "$DOMAIN_IP" != "$CURRENT_IP" ]; then
    print_warning "Domain $DOMAIN_NAME resolves to $DOMAIN_IP, but server IP is $CURRENT_IP"
    print_warning "DNS may not have propagated yet. Continue anyway? (y/N)"
    read -p "" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_success "Domain DNS is properly configured!"
fi

# =============================================================================
# STEP 2: Install Certbot & Get SSL Certificate
# =============================================================================
print_header "STEP 2: Installing SSL Certificate"

print_info "Installing Certbot..."
apt-get update -y
apt-get install -y certbot python3-certbot-nginx

print_info "Obtaining SSL certificate for $DOMAIN_NAME..."
certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME

if [ $? -eq 0 ]; then
    print_success "SSL certificate obtained successfully!"
else
    print_error "Failed to obtain SSL certificate"
    exit 1
fi

# =============================================================================
# STEP 3: Update Application Configuration
# =============================================================================
print_header "STEP 3: Updating Application Configuration"

PROJECT_DIR="/root/vaidya-vihar-diagnostic"

if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    print_info "Make sure to run deployment script first"
    exit 1
fi

cd $PROJECT_DIR

# Update .env file
print_info "Updating .env file with domain configuration..."
sed -i "s|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=[\"http://localhost:3000\", \"http://localhost:80\", \"http://$DOMAIN_NAME\", \"https://$DOMAIN_NAME\", \"http://www.$DOMAIN_NAME\", \"https://www.$DOMAIN_NAME\"]|" .env

print_success ".env file updated"

# =============================================================================
# STEP 4: Update Nginx Configuration
# =============================================================================
print_header "STEP 4: Updating Nginx Configuration"

# Backup current nginx config
cp nginx/nginx.conf nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# Update nginx configuration for domain
cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=auth:10m rate=5r/m;

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name $DOMAIN_NAME www.$DOMAIN_NAME;
        return 301 https://\$server_name\$request_uri;
    }

    # Main SSL server block
    server {
        listen 443 ssl http2;
        server_name $DOMAIN_NAME www.$DOMAIN_NAME;

        # SSL configuration
        ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;

        # SSL security settings
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";

            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # Backend API
        location /api/ {
            # Rate limiting for API
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            # API specific headers
            proxy_set_header X-Forwarded-Host \$server_name;
            proxy_set_header X-Forwarded-Port \$server_port;
        }

        # Backend direct access (for API docs, health checks)
        location /docs {
            proxy_pass http://backend/docs;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /health {
            proxy_pass http://backend/health;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Static files
        location /static/ {
            proxy_pass http://backend/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Security: Block access to sensitive files
        location ~ /\. {
            deny all;
        }

        location ~ \.(env|git|gitignore|htaccess|htpasswd)$ {
            deny all;
        }
    }
}
EOF

print_success "Nginx configuration updated for domain"

# =============================================================================
# STEP 5: Restart Services
# =============================================================================
print_header "STEP 5: Restarting Services"

print_info "Reloading Nginx configuration..."
nginx -t && systemctl reload nginx

print_info "Restarting application containers..."
docker compose restart

print_success "Services restarted"

# =============================================================================
# STEP 6: Verify Configuration
# =============================================================================
print_header "STEP 6: Verifying Configuration"

print_info "Testing HTTPS connection..."
HTTPS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN_NAME 2>/dev/null || echo "000")
if [ "$HTTPS_RESPONSE" = "200" ] || [ "$HTTPS_RESPONSE" = "301" ]; then
    print_success "HTTPS is working (Status: $HTTPS_RESPONSE)"
else
    print_warning "HTTPS may not be working yet (Status: $HTTPS_RESPONSE)"
fi

print_info "Testing HTTP to HTTPS redirect..."
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN_NAME 2>/dev/null || echo "000")
if [ "$HTTP_RESPONSE" = "301" ]; then
    print_success "HTTP to HTTPS redirect is working"
else
    print_warning "HTTP redirect may not be working (Status: $HTTP_RESPONSE)"
fi

# =============================================================================
# SETUP COMPLETE
# =============================================================================
print_header "🎉 DOMAIN & SSL SETUP COMPLETE!"

echo -e "\n${BLUE}🌐 Domain Configuration:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Domain:        $DOMAIN_NAME"
echo "  🔒 SSL:           Let's Encrypt (Auto-renewal enabled)"
echo "  🔄 Redirect:      HTTP → HTTPS"
echo "  📊 Status:        $(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN_NAME 2>/dev/null || echo "Check manually")"

echo -e "\n${BLUE}📱 Access URLs:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Frontend:      https://$DOMAIN_NAME"
echo "  🔧 Backend API:   https://$DOMAIN_NAME/api/"
echo "  📖 API Docs:      https://$DOMAIN_NAME/docs"
echo "  ❤️  Health:        https://$DOMAIN_NAME/health"

echo -e "\n${BLUE}🔧 Useful Commands:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔄 Reload Nginx:  nginx -t && systemctl reload nginx"
echo "  🔒 Renew SSL:     certbot renew"
echo "  📊 Check SSL:     curl -I https://$DOMAIN_NAME"
echo "  📝 View logs:     docker compose logs -f nginx"

echo -e "\n${YELLOW}⚠️  Important Notes:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • SSL certificates auto-renew every 90 days"
echo "  • Update your .env ALLOWED_ORIGINS if needed"
echo "  • Test all application features with HTTPS"
echo "  • Set up monitoring alerts for SSL expiry"

echo -e "\n${GREEN}🎯 Domain & SSL setup completed successfully!${NC}\n"

# Create a summary file
cat > /root/DOMAIN_SSL_SETUP.txt << EOF
================================================================
DOMAIN & SSL SETUP SUMMARY - $(date)
================================================================

Domain: $DOMAIN_NAME
Server IP: $CURRENT_IP
SSL Provider: Let's Encrypt
SSL Expiry: $(certbot certificates 2>/dev/null | grep -A 2 "Certificate Name" | grep -v "Certificate Name" | head -1 | xargs)

Access URLs:
- Frontend: https://$DOMAIN_NAME
- Backend API: https://$DOMAIN_NAME/api/
- API Docs: https://$DOMAIN_NAME/docs
- Health Check: https://$DOMAIN_NAME/health

SSL Auto-renewal: ENABLED
HTTP Redirect: ENABLED
Security Headers: ENABLED

Next Steps:
1. Test all application features
2. Update any hardcoded URLs in your application
3. Set up monitoring for SSL certificate expiry
4. Configure backup strategies

================================================================
EOF

print_info "Setup summary saved to /root/DOMAIN_SSL_SETUP.txt"
