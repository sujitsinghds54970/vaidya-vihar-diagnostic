# VaidyaVihar Diagnostic ERP - Deployment TODO

## Status: READY FOR DEPLOYMENT
## Server: Vultr (IP: YOUR_VULTR_IP)

---

## Phase 1: Server Preparation (Already Done)
- [x] Connect to Vultr server via SSH
- [x] Clone repository: `git clone https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic.git`
- [x] Navigate to project directory: `cd vaidya-vihar-diagnostic`

---

## Phase 2: Install Docker & Docker Compose
- [ ] Install Docker CE and Docker Compose Plugin
- [ ] Start and enable Docker service
- [ ] Verify installation with `docker --version` and `docker compose version`

---

## Phase 3: Configure Environment
- [ ] Create `.env` file with production settings
- [ ] Generate SSL certificates for HTTPS
- [ ] Create necessary directories (uploads, logs, ssl)

---

## Phase 4: Build & Start Services
- [ ] Build Docker images: `docker compose build --no-cache`
- [ ] Start all services: `docker compose up -d`
- [ ] Verify services are running: `docker compose ps`

---

## Phase 5: Database Initialization
- [ ] Wait for PostgreSQL to be healthy
- [ ] Run database migrations
- [ ] Seed initial data (admin user, branch)
- [ ] Verify database connection

---

## Phase 6: Testing & Verification
- [ ] Test backend API: `curl http://localhost:8000/health`
- [ ] Test frontend access: `http://YOUR_VULTR_IP`
- [ ] Test API docs: `http://YOUR_VULTR_IP:8000/docs`
- [ ] Login with default credentials: admin / admin123

---

## Phase 7: Post-Deployment Configuration
- [ ] Configure firewall rules (ufw)
- [ ] Set up automated backups
- [ ] Configure domain (optional)
- [ ] Set up SSL with Let's Encrypt (optional)

---

## Quick Commands Reference

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop all services
docker compose down

# Update and redeploy
git pull origin main
docker compose down
docker compose build --no-cache
docker compose up -d

# Backup database
docker compose exec postgres pg_dump -U vaidya_user vaidya_vihar_db > backup_$(date +%Y%m%d).sql

# SSH into container
docker compose exec backend sh
docker compose exec frontend sh
docker compose exec postgres psql -U vaidya_user -d vaidya_vihar_db
```

---

## Service URLs (After Deployment)

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://YOUR_VULTR_IP | 80 |
| Backend API | http://YOUR_VULTR_IP:8000 | 8000 |
| API Docs | http://YOUR_VULTR_IP:8000/docs | 8000 |
| Health Check | http://YOUR_VULTR_IP/health | 80 |

---

## Default Credentials
- **Username:** admin
- **Password:** admin123

---

## Common Issues & Solutions

### Port 80/443 not working?
```bash
ufw allow 80
ufw allow 443
ufw allow 8000
ufw status
```

### Frontend not loading?
```bash
docker compose logs frontend
docker compose up -d --build frontend
```

### Database connection failed?
```bash
docker compose logs postgres
sleep 20
docker compose exec backend python -c "from app.database import engine; engine.connect()"
```

---

## Created: $(date)
## Last Updated: $(date)

