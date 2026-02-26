#!/bin/bash

# =============================================================================
# DigitalOcean Droplet Initial Setup Script
# =============================================================================
# Run this script immediately after creating your DigitalOcean droplet
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

print_header "🏥 VAIDYAVIHAR - DIGITALOCEAN DROPLET SETUP"
echo -e "${YELLOW}🚀 Starting DigitalOcean droplet configuration...${NC}\n"

# =============================================================================
# STEP 1: Update System
# =============================================================================
print_header "STEP 1: Updating System"

print_info "Updating package lists..."
apt-get update -y

print_info "Upgrading system packages..."
apt-get upgrade -y

print_info "Installing essential packages..."
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    vim \
    ufw \
    fail2ban \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release

print_success "System updated and essential packages installed"

# =============================================================================
# STEP 2: Configure Firewall
# =============================================================================
print_header "STEP 2: Configuring Firewall"

print_info "Setting up UFW firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force reload

print_info "Configuring fail2ban for SSH protection..."
systemctl enable fail2ban
systemctl start fail2ban

print_success "Firewall configured and fail2ban enabled"

# =============================================================================
# STEP 3: Create Non-Root User (Optional but Recommended)
# =============================================================================
print_header "STEP 3: Creating Deployment User"

# Create deployment user
if id "deploy" &>/dev/null; then
    print_warning "User 'deploy' already exists"
else
    print_info "Creating deployment user..."
    useradd -m -s /bin/bash deploy
    usermod -aG sudo deploy

    print_info "Setting up SSH for deploy user..."
    mkdir -p /home/deploy/.ssh
    cp /root/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
    chown -R deploy:deploy /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    chmod 600 /home/deploy/.ssh/authorized_keys 2>/dev/null || true

    print_success "Deployment user created"
    print_info "You can now login as: ssh deploy@YOUR_DROPLET_IP"
fi

# =============================================================================
# STEP 4: Install Docker
# =============================================================================
print_header "STEP 4: Installing Docker"

if command -v docker &> /dev/null; then
    print_success "Docker is already installed: $(docker --version)"
else
    print_info "Installing Docker CE..."

    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker CE
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Start and enable Docker
    systemctl start docker
    systemctl enable docker

    # Add users to docker group
    usermod -aG docker root
    usermod -aG docker deploy 2>/dev/null || true

    print_success "Docker installed successfully: $(docker --version)"
    print_success "Docker Compose Plugin installed: $(docker compose version)"
fi

# =============================================================================
# STEP 5: Install DigitalOcean Monitoring Agent
# =============================================================================
print_header "STEP 5: Installing DigitalOcean Monitoring"

if systemctl is-active --quiet do-agent; then
    print_success "DigitalOcean monitoring agent is already running"
else
    print_info "Installing DigitalOcean monitoring agent..."
    curl -sSL https://repos.insights.digitalocean.com/install.sh | bash
    print_success "DigitalOcean monitoring agent installed"
fi

# =============================================================================
# STEP 6: Configure SSH Security
# =============================================================================
print_header "STEP 6: Hardening SSH Security"

# Backup original sshd_config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Configure SSH
cat >> /etc/ssh/sshd_config << EOF

# Security hardening
PermitRootLogin no
PasswordAuthentication no
X11Forwarding no
PermitEmptyPasswords no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# Allow only deploy user
AllowUsers deploy
EOF

print_info "Restarting SSH service..."
systemctl reload sshd

print_success "SSH security hardened"
print_warning "Root login disabled. Use 'deploy' user for future logins."

# =============================================================================
# STEP 7: Set Up Swap Space (Optional)
# =============================================================================
print_header "STEP 7: Setting Up Swap Space"

if [ -f /swapfile ]; then
    print_success "Swap space already configured"
else
    print_info "Creating 1GB swap file..."
    fallocate -l 1G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile

    # Make permanent
    echo '/swapfile none swap sw 0 0' >> /etc/fstab

    print_success "Swap space configured (1GB)"
fi

# =============================================================================
# STEP 8: Install Additional Tools
# =============================================================================
print_header "STEP 8: Installing Additional Tools"

print_info "Installing monitoring and backup tools..."
apt-get install -y \
    iotop \
    ncdu \
    tmux \
    screen \
    postgresql-client \
    redis-tools

print_success "Additional tools installed"

# =============================================================================
# SETUP COMPLETE
# =============================================================================
print_header "🎉 DIGITALOCEAN DROPLET SETUP COMPLETE!"

echo -e "\n${BLUE}📊 System Information:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🖥️  OS:           $(lsb_release -d | cut -f2)"
echo "  🐳 Docker:       $(docker --version)"
echo "  📦 Compose:      $(docker compose version)"
echo "  🔥 Firewall:     $(ufw status | grep -c "ALLOW") rules active"
echo "  🔄 Swap:         $(free -h | grep Swap | awk '{print $2}')"
echo "  👤 Users:        $(getent passwd | grep -c "/bin/bash") users with shell access"

echo -e "\n${BLUE}🔐 Security Status:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ❌ Root SSH:     Disabled"
echo "  ❌ Password Auth: Disabled"
echo "  ✅ Key Auth:     Required"
echo "  ✅ Firewall:     Active"
echo "  ✅ Fail2Ban:     Active"
echo "  ✅ Monitoring:   Active"

echo -e "\n${BLUE}🚀 Next Steps:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1. 🔑 Login with deploy user: ssh deploy@YOUR_DROPLET_IP"
echo "  2. 📦 Deploy application: ./scripts/deploy-digitalocean.sh"
echo "  3. 🌐 Point domain to: $(curl -s http://checkip.amazonaws.com)"
echo "  4. 🔒 Setup SSL: certbot --nginx -d yourdomain.com"

echo -e "\n${YELLOW}⚠️  Important:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • Keep your SSH private key secure!"
echo "  • Change default passwords after deployment!"
echo "  • Set up automated backups!"
echo "  • Monitor server resources regularly!"

echo -e "\n${GREEN}🎯 Ready for deployment!${NC}\n"

# =============================================================================
# Optional: Create Quick Reference
# =============================================================================
cat > /root/DIGITALOCEAN_SETUP_INFO.txt << EOF
================================================================
DIGITALOCEAN DROPLET SETUP - $(date)
================================================================

Droplet IP: $(curl -s http://checkip.amazonaws.com)
SSH User: deploy
SSH Key: Required (password auth disabled)

Security:
- Root login: DISABLED
- Password auth: DISABLED
- Firewall: ACTIVE (ports 22,80,443,8000)
- Fail2Ban: ACTIVE
- Monitoring: ACTIVE

Next Steps:
1. Login: ssh deploy@YOUR_IP
2. Deploy: ./scripts/deploy-digitalocean.sh
3. Domain: Point A record to $(curl -s http://checkip.amazonaws.com)
4. SSL: certbot --nginx -d yourdomain.com

Useful Commands:
- View logs: docker compose logs -f
- Restart: docker compose restart
- Update: git pull && docker compose build --no-cache && docker compose up -d
- Backup: docker compose exec postgres pg_dump -U vaidya_user vaidya_vihar_db > backup.sql

================================================================
EOF

print_info "Setup information saved to /root/DIGITALOCEAN_SETUP_INFO.txt"
