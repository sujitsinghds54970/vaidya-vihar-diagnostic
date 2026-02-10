#!/bin/bash

# SSL Certificate Generation Script for VaidyaVihar Diagnostic ERP
# Generates self-signed certificates for development or Let's Encrypt for production

set -e

echo "🔐 VaidyaVihar SSL Certificate Generator"
echo "========================================"
echo ""

# Create SSL directory if it doesn't exist
mkdir -p nginx/ssl

# Function to generate self-signed certificate
generate_self_signed() {
    echo "📝 Generating self-signed SSL certificate..."
    echo ""
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=IN/ST=State/L=City/O=VaidyaVihar Diagnostic/OU=IT/CN=localhost"
    
    echo "✅ Self-signed certificate generated successfully!"
    echo "   Certificate: nginx/ssl/cert.pem"
    echo "   Private Key: nginx/ssl/key.pem"
    echo ""
    echo "⚠️  Note: This is a self-signed certificate for development only."
    echo "   Browsers will show a security warning. For production, use Let's Encrypt."
}

# Function to setup Let's Encrypt
setup_letsencrypt() {
    echo "🌐 Setting up Let's Encrypt certificate..."
    echo ""
    
    read -p "Enter your domain name (e.g., vaidyavihar.com): " DOMAIN
    read -p "Enter your email address: " EMAIL
    
    if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
        echo "❌ Domain and email are required!"
        exit 1
    fi
    
    echo ""
    echo "Installing certbot..."
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        echo "Installing certbot..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install certbot
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update
            sudo apt-get install -y certbot
        else
            echo "❌ Unsupported OS. Please install certbot manually."
            exit 1
        fi
    fi
    
    echo ""
    echo "Generating Let's Encrypt certificate..."
    echo "⚠️  Make sure port 80 is accessible from the internet!"
    echo ""
    
    sudo certbot certonly --standalone \
        -d "$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive
    
    # Copy certificates to nginx directory
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" nginx/ssl/cert.pem
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" nginx/ssl/key.pem
    sudo chmod 644 nginx/ssl/cert.pem
    sudo chmod 600 nginx/ssl/key.pem
    
    echo ""
    echo "✅ Let's Encrypt certificate generated successfully!"
    echo "   Certificate: nginx/ssl/cert.pem"
    echo "   Private Key: nginx/ssl/key.pem"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Update nginx/nginx.conf with your domain name"
    echo "   2. Uncomment the SSL server block"
    echo "   3. Restart nginx: docker-compose restart nginx"
    echo ""
    echo "🔄 Certificate renewal:"
    echo "   Certificates expire in 90 days. Set up auto-renewal:"
    echo "   sudo certbot renew --dry-run"
}

# Main menu
echo "Select certificate type:"
echo "1) Self-signed (Development)"
echo "2) Let's Encrypt (Production)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        generate_self_signed
        ;;
    2)
        setup_letsencrypt
        ;;
    *)
        echo "❌ Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "🎉 SSL setup complete!"
echo ""
echo "📋 To enable HTTPS:"
echo "   1. Edit nginx/nginx.conf"
echo "   2. Uncomment the SSL server block (lines starting with #)"
echo "   3. Update server_name with your domain"
echo "   4. Restart nginx: docker-compose restart nginx"
echo ""
