#!/bin/bash

# Database Backup Script for VaidyaVihar Diagnostic ERP
# Creates automated backups of PostgreSQL database

set -e

echo "💾 VaidyaVihar Database Backup"
echo "=============================="
echo ""

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="vaidya_vihar_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if PostgreSQL container is running
if ! docker-compose ps postgres | grep -q "Up"; then
    print_error "PostgreSQL container is not running!"
    echo "Start it with: docker-compose up -d postgres"
    exit 1
fi

print_info "Starting database backup..."

# Create backup
docker-compose exec -T postgres pg_dump -U vaidya_user vaidya_vihar_db | gzip > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    print_success "Backup created successfully!"
    echo "   File: $BACKUP_DIR/$BACKUP_FILE"
    echo "   Size: $BACKUP_SIZE"
else
    print_error "Backup failed!"
    exit 1
fi

# Clean up old backups
print_info "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "vaidya_vihar_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/vaidya_vihar_backup_*.sql.gz 2>/dev/null | wc -l)
print_success "Cleanup complete. Total backups: $BACKUP_COUNT"

echo ""
echo "📋 Recent backups:"
ls -lh "$BACKUP_DIR"/vaidya_vihar_backup_*.sql.gz | tail -5

echo ""
print_success "Backup process completed!"
