#!/bin/bash

# Database Restore Script for VaidyaVihar Diagnostic ERP
# Restores PostgreSQL database from backup

set -e

echo "🔄 VaidyaVihar Database Restore"
echo "==============================="
echo ""

# Configuration
BACKUP_DIR="backups"

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    print_error "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# List available backups
echo "📋 Available backups:"
echo ""
backups=($(ls -1t "$BACKUP_DIR"/vaidya_vihar_backup_*.sql.gz 2>/dev/null))

if [ ${#backups[@]} -eq 0 ]; then
    print_error "No backups found in $BACKUP_DIR"
    exit 1
fi

# Display backups with numbers
for i in "${!backups[@]}"; do
    backup_file="${backups[$i]}"
    backup_size=$(du -h "$backup_file" | cut -f1)
    backup_date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup_file" 2>/dev/null || stat -c "%y" "$backup_file" 2>/dev/null | cut -d'.' -f1)
    echo "$((i+1))) $(basename "$backup_file") - $backup_size - $backup_date"
done

echo ""
read -p "Enter backup number to restore (or 'q' to quit): " choice

if [ "$choice" = "q" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Validate choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#backups[@]} ]; then
    print_error "Invalid choice!"
    exit 1
fi

BACKUP_FILE="${backups[$((choice-1))]}"

echo ""
print_warning "WARNING: This will replace the current database!"
print_warning "All existing data will be lost!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Check if PostgreSQL container is running
if ! docker-compose ps postgres | grep -q "Up"; then
    print_error "PostgreSQL container is not running!"
    echo "Start it with: docker-compose up -d postgres"
    exit 1
fi

print_info "Stopping backend service..."
docker-compose stop backend

print_info "Dropping existing database..."
docker-compose exec -T postgres psql -U vaidya_user -d postgres -c "DROP DATABASE IF EXISTS vaidya_vihar_db;"

print_info "Creating new database..."
docker-compose exec -T postgres psql -U vaidya_user -d postgres -c "CREATE DATABASE vaidya_vihar_db;"

print_info "Restoring database from backup..."
gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U vaidya_user -d vaidya_vihar_db

if [ $? -eq 0 ]; then
    print_success "Database restored successfully!"
else
    print_error "Database restore failed!"
    exit 1
fi

print_info "Starting backend service..."
docker-compose start backend

echo ""
print_success "Restore process completed!"
echo ""
echo "📋 Restored from: $(basename "$BACKUP_FILE")"
echo ""
print_warning "Please verify the application is working correctly."
