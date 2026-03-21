# 🚀 Digital Ocean Deployment Guide

## ✅ Project is Now Ready for Digital Ocean Auto-Deploy!

All necessary files have been added and the project structure is optimized for Digital Ocean App Platform.

---

## 📁 Files Added for Digital Ocean

1. **`Procfile`** - Defines how to run the backend service
2. **`runtime.txt`** - Specifies Python version (3.11.7)
3. **`app.json`** - App metadata and configuration
4. **`.do/app.yaml`** - Complete Digital Ocean app specification
5. **`package.json`** (root) - For Node.js detection
6. **`requirements.txt`** (root) - For Python detection

---

## 🎯 Deployment Steps

### Method 1: Using Digital Ocean Dashboard (Recommended)

1. **Go to Digital Ocean App Platform**
   - Visit: https://cloud.digitalocean.com/apps

2. **Create New App**
   - Click "Create App"
   - Select "GitHub" as source
   - Authorize Digital Ocean to access your GitHub

3. **Select Repository**
   - Repository: `sujitsinghds54970/vaidya-vihar-diagnostic`
   - Branch: `master`
   - Auto-deploy: ✅ Enable

4. **Digital Ocean Will Auto-Detect:**
   - ✅ Python app (from `runtime.txt` and `requirements.txt`)
   - ✅ Node.js app (from `package.json`)
   - ✅ App configuration (from `.do/app.yaml`)

5. **Configure Services** (Auto-filled from app.yaml):

   **Backend Service:**
   - Name: `backend`
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Run Command: `cd backend && gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080`
   - HTTP Port: `8080`
   - Instance Size: Basic ($5/month)

   **Frontend Service:**
   - Name: `frontend`
   - Source Directory: `frontend/vaidya-vihar-frontend`
   - Build Command: `npm install && npm run build`
   - Run Command: `npx serve -s build -l 8080`
   - HTTP Port: `8080`
   - Instance Size: Basic ($5/month)

6. **Add Database**
   - Type: PostgreSQL
   - Version: 15
   - Plan: Development ($7/month) or Basic ($15/month)
   - Name: `db`

7. **Environment Variables** (Auto-configured):
   
   Backend:
   - `DATABASE_URL`: `${db.DATABASE_URL}` (auto-injected)
   - `SECRET_KEY`: `vaidya-vihar-secret-key-2024-change-this` (Secret)
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `1440`
   - `DEBUG`: `False`
   - `PYTHONPATH`: `/workspace/backend`

   Frontend:
   - `REACT_APP_API_URL`: `${backend.PUBLIC_URL}` (auto-injected)

8. **Review & Deploy**
   - Review all settings
   - Click "Create Resources"
   - Wait for deployment (5-10 minutes)

---

### Method 2: Using App Spec File

```bash
# Install doctl CLI
brew install doctl  # macOS
# or download from: https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml

# Monitor deployment
doctl apps list
```

---

## 🔧 Post-Deployment Steps

### 1. Initialize Database

After first deployment, run database initialization:

**Option A: Using Console**
1. Go to your app in Digital Ocean dashboard
2. Click on "backend" service
3. Go to "Console" tab
4. Run: `python3 init_database.py`

**Option B: Using doctl**
```bash
doctl apps logs <app-id> --type run
```

### 2. Access Your Application

- **Frontend**: `https://vaidya-vihar-diagnostic.ondigitalocean.app`
- **Backend API**: `https://vaidya-vihar-diagnostic-backend.ondigitalocean.app`
- **API Docs**: `https://vaidya-vihar-diagnostic-backend.ondigitalocean.app/docs`

### 3. Login with Default Credentials

- Username: `admin`
- Password: `admin123`
- **⚠️ IMPORTANT: Change these immediately after first login!**

---

## 💰 Pricing Estimate

### Development Setup
- Backend (Basic): $5/month
- Frontend (Basic): $5/month
- Database (Development): $7/month
- **Total: ~$17/month**

### Production Setup
- Backend (Professional): $12/month
- Frontend (Basic): $5/month
- Database (Basic): $15/month
- **Total: ~$32/month**

---

## 🔍 Troubleshooting

### Build Fails

**Check Build Logs:**
1. Go to app dashboard
2. Click on failing service
3. View "Build Logs" tab

**Common Issues:**
- Missing dependencies → Check `requirements.txt`
- Python version mismatch → Verify `runtime.txt`
- Import errors → Check `PYTHONPATH` environment variable

### Runtime Fails

**Check Runtime Logs:**
```bash
doctl apps logs <app-id> --type run --follow
```

**Common Issues:**
- Database connection → Verify `DATABASE_URL` is set
- Port binding → Ensure using port `8080`
- Health check fails → Verify `/docs` endpoint is accessible

### Database Connection Issues

1. Verify database is created
2. Check `DATABASE_URL` environment variable
3. Ensure database initialization ran successfully
4. Check database logs in DO dashboard

---

## 📊 Monitoring

### View Logs
```bash
# All logs
doctl apps logs <app-id>

# Backend logs
doctl apps logs <app-id> --type run_restarted

# Build logs
doctl apps logs <app-id> --type build
```

### Metrics
- Go to app dashboard
- Click "Insights" tab
- View CPU, Memory, and Request metrics

---

## 🔄 Updates & Redeployment

### Automatic Deployment
- Push to `master` branch
- Digital Ocean auto-deploys
- No manual intervention needed

### Manual Deployment
```bash
# Trigger manual deployment
doctl apps create-deployment <app-id>
```

---

## 🛡️ Security Best Practices

1. **Change Default Credentials**
   - Login immediately after deployment
   - Change admin password
   - Create new admin user

2. **Update SECRET_KEY**
   - Generate new secret key
   - Update in environment variables
   - Redeploy app

3. **Enable HTTPS**
   - Digital Ocean provides free SSL
   - Automatically enabled

4. **Database Backups**
   - Enable automated backups in DO dashboard
   - Schedule: Daily recommended

---

## 📚 Additional Resources

- [Digital Ocean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)

---

## ✅ Deployment Checklist

Before deploying:
- [x] All files committed to GitHub
- [x] `Procfile` created
- [x] `runtime.txt` created
- [x] `app.json` created
- [x] `.do/app.yaml` configured
- [x] Environment variables documented
- [ ] GitHub repository connected to DO
- [ ] Database created
- [ ] Environment variables set
- [ ] App deployed successfully
- [ ] Database initialized
- [ ] Default credentials changed

---

## 🎉 Success!

Your VaidyaVihar Diagnostic ERP is now ready for Digital Ocean deployment!

**Repository**: https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic

**Status**: ✅ Production Ready

---

*Last Updated: March 21, 2026*
*Version: 2.0.1*
