# 🚗 Fleet Health Monitor - Complete Application

A modern Fleet Management System with Microsoft Entra ID authentication, AI-powered chatbot, and Salesforce integration.

## ✨ Features

### 🔐 Authentication
- **Microsoft Entra ID OAuth** - Secure enterprise authentication
- **Demo Login** - Test without Microsoft setup
- **Session Management** - 24-hour session expiry
- **Protected Routes** - All pages require authentication

### 📊 Dashboard
- Real-time vehicle statistics
- Status breakdown (Allocated, Spare, Maintenance, etc.)
- Quick-access navigation
- AI Chat button for fleet queries

### 🤖 AI Chatbot
- **Groq-powered** - Fast AI responses
- **Few-shot Learning** - Accurate intent classification
- **Live Data** - Queries Salesforce in real-time
- **Session Management** - Multiple chat conversations
- **Message History** - Persistent chat sessions

### 📤 Vehicle Management
- **Upload Vehicles** - Add new vehicles with photos
- **Assets Gallery** - View all vehicles with details
- **Filter by Status** - Find vehicles by status
- **Vehicle Details** - Complete vehicle information

### 🌐 Integrations
- **Salesforce CRM** - Direct data sync
- **Webfleet** - Vehicle tracking integration
- **Groq AI** - Advanced chatbot capabilities
- **Microsoft Graph** - User profile integration

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
Node.js 16+
npm or yarn
Salesforce account
Microsoft Azure account (optional)
```

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.template .env

# Edit .env with your credentials
# SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, etc.

# Start backend
python app.py
```

**Expected output:**
```
✅ Connected to Salesforce
✅ Groq Chat service initialized
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. Frontend Setup

```bash
# In root directory (not backend/)
npm install
npm run dev
```

**Expected output:**
```
VITE v4.x.x ready in 123 ms
➜ Local: http://localhost:5173/
```

### 3. Access Application
- Open browser: `http://localhost:5173`
- Click "Sign in with Microsoft" or "Demo Login"
- Explore dashboard and features

---

## 📋 Application Flow

```
┌─────────────────────────────────────────────┐
│           LOGIN PAGE (/login)               │
│  ┌─────────────────────────────────────┐   │
│  │ Sign with Microsoft / Demo Login    │   │
│  └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │ Authentication
               ▼
┌─────────────────────────────────────────────┐
│      MAIN LAYOUT WITH SIDEBAR               │
│  ┌─────────────────────────────────────┐   │
│  │ Dashboard  Upload  Assets  Webfleet │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   DASHBOARD (Default Home)          │   │
│  │   • Stats Cards                     │   │
│  │   • AI Chat Button                  │   │
│  │   • Quick Navigation                │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   UPLOAD PAGE                       │   │
│  │   • Add Vehicles                    │   │
│  │   • Attach Photos                   │   │
│  │   • Verify Data                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   ASSETS GALLERY                    │   │
│  │   • View All Vehicles               │   │
│  │   • Filter by Status                │   │
│  │   • Vehicle Details                 │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   CHATBOT (via AI Chat button)      │   │
│  │   • Multi-session support           │   │
│  │   • Live Salesforce queries         │   │
│  │   • Quick question templates        │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🎯 Routes & Pages

| Route | Page | Description |
|-------|------|-------------|
| `/login` | Login | Authentication entry point |
| `/` | Dashboard | Main dashboard with stats |
| `/fleet-dashboard` | Dashboard | Alias for dashboard |
| `/upload` | Upload | Add/manage vehicles |
| `/assets` | Assets Gallery | View all vehicles |
| `/assets/:id` | Asset Detail | Single vehicle details |
| `/webfleet` | Webfleet | Vehicle tracking |
| `/chatbot` | Chatbot | AI assistant (public) |

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# SALESFORCE
SF_USERNAME=your_email@company.com
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_token
SF_DOMAIN=login  # or 'test' for sandbox

# MICROSOFT AUTH
MICROSOFT_CLIENT_ID=xxxxx
MICROSOFT_CLIENT_SECRET=xxxxx
MICROSOFT_TENANT_ID=common

# URLS
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# OPTIONAL: GROQ AI
GROQ_API_KEY=gsk_xxxxx

# SERVER
PORT=8000
```

### Setup Microsoft OAuth

1. **Azure Portal → Entra ID → App Registrations**
2. **Click "New Registration"**
   - Name: Fleet Health Monitor
   - Redirect URI: `http://localhost:8000/api/auth/callback/microsoft`
3. **Copy Client ID & Secret to .env**
4. **API Permissions → Add "User.Read"**

---

## 🤖 Chatbot Usage

### Quick Questions
- "How many vehicles are there?"
- "Tell me about VEH-439"
- "Who is driving that vehicle?"
- "Show me spare vehicles"
- "What vehicles need maintenance?"

### Intent Classification
The AI understands:
- **count_all_vehicles** - Total fleet size
- **get_vehicle_info** - Vehicle details
- **get_vehicle_driver** - Current driver
- **get_spare_vehicles** - Available vehicles
- **get_maintenance_schedule** - Service due
- **list_all_drivers** - All drivers
- **get_vehicles_by_location** - Location filter

### Features
- ✅ Multi-session support
- ✅ Message history persistence
- ✅ Copy message to clipboard
- ✅ Live Salesforce data
- ✅ Natural language responses

---

## 📊 Dashboard Statistics

- **Total Vehicles** - All vehicles in system
- **Allocated** - Currently assigned (green)
- **In Garage** - Under maintenance (orange)
- **Due for Service** - Upcoming maintenance (red)
- **Spare Ready** - Available vehicles (purple)
- **Reserved** - Reserved vehicles (yellow)
- **Written Off** - Decommissioned (gray)

Click any card to filter assets by that status.

---

## 🔍 Troubleshooting

### Backend Issues

**"No such column 'Description__c'"**
```
Solution: Use __c suffix for custom fields
File: backend/salesforce_service.py
```

**Connection refused**
```
Check: Is backend running on port 8000?
Test: curl http://localhost:8000/api/health
```

**Salesforce authentication failed**
```
Check:
1. SF_USERNAME and password are correct
2. Security token is appended to password
3. IP whitelist allows your IP (if applicable)
```

### Frontend Issues

**Blank login page**
```
Check:
1. Backend is running: http://localhost:8000
2. CORS is enabled
3. Browser console for errors
```

**Chatbot returns errors**
```
Check:
1. Groq API key is set in .env
2. Salesforce connection is active
3. Backend logs: python app.py
```

---

## 📦 Project Structure

```
fleet-health-monitor/
├── backend/
│   ├── app.py                 # FastAPI app
│   ├── routes/
│   │   ├── auth.py           # Authentication
│   │   ├── chat.py           # Chatbot
│   │   ├── assets.py         # Asset management
│   │   ├── vehicles.py       # Vehicle endpoints
│   │   └── ...
│   ├── salesforce_service.py # Salesforce connector
│   ├── groq_service.py       # AI chatbot engine
│   ├── requirements.txt      # Python deps
│   └── .env.template         # Config template
│
├── src/
│   ├── pages/
│   │   ├── Login.tsx         # Authentication
│   │   ├── Dashboard.tsx     # Main dashboard
│   │   ├── chatbot.tsx       # Chatbot UI
│   │   ├── Upload.tsx        # Vehicle upload
│   │   ├── AssetsGallery.tsx # Asset list
│   │   └── ...
│   ├── components/
│   │   ├── layout/
│   │   │   └── MainLayout.tsx    # App layout
│   │   └── ui/              # UI components
│   ├── App.tsx              # App router
│   └── main.tsx             # Entry point
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## 🚀 Deployment

### Frontend (React)
```bash
npm run build
# Deploy 'dist/' folder to:
# - Vercel, Netlify, Azure Static Web Apps, etc.
```

### Backend (FastAPI)
```bash
# Docker
docker build -t fleet-api .
docker run -p 8000:8000 fleet-api

# Or traditional:
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📞 Support & Debugging

### Enable Logging
```bash
# Backend
export LOG_LEVEL=DEBUG
python app.py

# Frontend
# Check browser console: F12 → Console tab
```

### API Documentation
- FastAPI Auto-docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Common Issues
1. **Port 8000 in use**: `lsof -i :8000` (Linux/Mac) or `netstat -ano | findstr :8000` (Windows)
2. **Module not found**: `pip install -r requirements.txt`
3. **CORS errors**: Backend allows all origins in dev mode

---

## 📝 Security Notes

- ✅ Microsoft OAuth for enterprise auth
- ✅ Session tokens expire after 24h
- ✅ Protected API endpoints
- ✅ Secure credential storage
- ⚠️ Never commit .env file to Git
- ⚠️ Use environment variables in production

---

## 📄 License & Credits

Built with:
- **FastAPI** - Modern Python framework
- **React** - UI library
- **Tailwind CSS** - Styling
- **Groq API** - AI chatbot
- **Salesforce** - CRM integration
- **Microsoft Entra ID** - Authentication

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Salesforce API](https://developer.salesforce.com)
- [Groq Documentation](https://console.groq.com)

---

**Happy fleet managing! 🚗✨**

For questions or issues, check backend logs or browser console for detailed error messages.
