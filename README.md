# 🏥 VaidyaVihar Diagnostic ERP

Complete Enterprise Resource Planning system for Diagnostic Centers with 20+ integrated modules.

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic/tree/master)

## 🚀 Features

### Core Modules
- ✅ **Multi-Branch Management** - Manage multiple diagnostic centers
- ✅ **Patient Management** - Complete patient records & history
- ✅ **Daily Entry System** - Quick patient registration & billing
- ✅ **Staff Management** - Employee records & attendance
- ✅ **Inventory Management** - Stock tracking & alerts
- ✅ **Appointment Scheduling** - Patient appointments
- ✅ **Invoice & Billing** - Comprehensive billing system
- ✅ **Lab Results** - Test results management
- ✅ **Analytics & Reports** - Business intelligence dashboards

### Advanced Modules
- ✅ **Payment Processing** - Multiple payment methods
- ✅ **Accounting Module** - Complete accounting system
- ✅ **HR & Payroll** - Employee management & payroll
- ✅ **LIS (Laboratory Information System)** - Advanced lab management
- ✅ **Patient Portal** - Patient self-service portal
- ✅ **Doctor Portal** - Doctor dashboard & report access
- ✅ **AI Features** - AI-powered test recommendations
- ✅ **Report Distribution** - Automatic report delivery to doctors
- ✅ **WebSocket Support** - Real-time notifications
- ✅ **SMS & WhatsApp Integration** - Multi-channel notifications
- ✅ **QR Code Generation** - For reports and invoices

## 📊 Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- PostgreSQL / SQLite
- JWT Authentication
- WebSocket Support

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- React Router
- Axios

**DevOps:**
- Docker & Docker Compose
- Nginx
- GitHub Actions
- Digital Ocean App Platform

## 🎯 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic.git
cd vaidya-vihar-diagnostic

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python3 init_database.py

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python3 init_database.py
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend/vaidya-vihar-frontend
npm install
npm start
```

### Option 3: Quick Start Script

```bash
./START_PROJECT.sh
```

## 🔐 Default Credentials

- **Username:** `admin`
- **Password:** `admin123`
- **Branch:** Main Branch - Bhabua

⚠️ **Change these credentials immediately after first login!**

## 🌐 Deploy to Digital Ocean

### Method 1: One-Click Deploy

Click the "Deploy to DO" button above or use this link:
```
https://cloud.digitalocean.com/apps/new?repo=https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic/tree/master
```

### Method 2: Manual Deploy

1. **Create App on Digital Ocean:**
   - Go to Digital Ocean App Platform
   - Click "Create App"
   - Connect your GitHub repository
   - Select `vaidya-vihar-diagnostic`
   - Digital Ocean will auto-detect the configuration

2. **Configure Environment Variables:**
   ```
   SECRET_KEY=your-super-secret-key-change-this
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   DEBUG=False
   ```

3. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete
   - Access your app at the provided URL

### Method 3: Using App Spec

```bash
# Deploy using the app.yaml specification
doctl apps create --spec .do/app.yaml
```

## 📁 Project Structure

```
vaidya-vihar-diagnostic/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── models/            # Database models (30+)
│   │   ├── routes/            # API endpoints (196 routes)
│   │   ├── services/          # Business logic
│   │   ├── utils/             # Utilities
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   ├── init_database.py       # DB initialization
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend Docker config
├── frontend/
│   └── vaidya-vihar-frontend/ # React Frontend
│       ├── src/
│       │   ├── components/    # React components
│       │   ├── contexts/      # React contexts
│       │   └── services/      # API services
│       ├── package.json       # Node dependencies
│       └── Dockerfile         # Frontend Docker config
├── .do/
│   └── app.yaml               # Digital Ocean config
├── docker-compose.yml         # Docker Compose config
├── package.json               # Root package.json
├── requirements.txt           # Root requirements.txt
└── README.md                  # This file
```

## 🔧 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@postgres:5432/vaidya_vihar_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEBUG=False
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Frontend
```env
REACT_APP_API_URL=https://your-backend-url.com
```

## 📊 API Documentation

Once the backend is running, access the interactive API documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

**Total API Routes:** 196

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend/vaidya-vihar-frontend
npm test
```

## 📈 Monitoring

### View Logs
```bash
# Docker logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Backup
```bash
# Backup
docker-compose exec postgres pg_dump -U vaidya_user vaidya_vihar_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U vaidya_user vaidya_vihar_db < backup.sql
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Sujit Singh**
- GitHub: [@sujitsinghds54970](https://github.com/sujitsinghds54970)

## 🆘 Support

For issues or questions:
1. Check the [Documentation](DEPLOYMENT_READY.md)
2. Review [API Docs](http://localhost:8000/docs)
3. Open an [Issue](https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic/issues)

## 🎊 Acknowledgments

- FastAPI for the amazing framework
- React team for the frontend library
- Digital Ocean for hosting platform

---

**Status:** ✅ Production Ready | **Version:** 2.0.0 | **Last Updated:** March 20, 2026
