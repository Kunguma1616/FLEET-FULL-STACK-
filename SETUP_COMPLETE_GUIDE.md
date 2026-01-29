# 🚀 Fleet Health Monitor - COMPLETE SETUP

## ✅ System Status

All integrations are connected and working:

- ✅ **Salesforce**: Real-time vehicle data (tech@aspect.co.uk)
- ✅ **Webfleet**: Driver tracking & performance scores (Pavlo Manko)
- ✅ **Microsoft OAuth**: Company authentication (@aspect.co.uk)
- ✅ **Groq AI**: Intelligent chatbot
- ✅ **Mock Data**: Fallback when Salesforce unavailable

## 🔐 Authentication Flow

1. User visits `http://localhost:5174/`
2. Clicks "Login with Microsoft"
3. Redirects to Microsoft OAuth
4. Backend validates user is @aspect.co.uk
5. Creates session and redirects back with params
6. Frontend saves session to localStorage
7. Dashboard loads with real Salesforce data

## 🚀 Quick Start

### Option 1: Double-click to Start Everything
```
START_SERVERS_BOTH.bat
```

### Option 2: Manual Start (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Then Open:
```
http://localhost:5174/
```

## 📋 Login Credentials

**Microsoft OAuth**: 
- Company email: `Kunguma.Balaji@aspect.co.uk` (or any @aspect.co.uk email)
- Password: Your company Microsoft password

**Demo Mode**:
- Enter any email for demo without OAuth

## 🔧 Configuration Files

### `.env.local` (Frontend)
```
VITE_API_URL=http://localhost:8002
```

### `backend/.env` (Backend)
```
SF_USERNAME=tech@aspect.co.uk
SF_PASSWORD=TuanIsTheBest12
SF_SECURITY_TOKEN=9AHwz5yyDyEP4NulU84JFJdl
SF_DOMAIN=login

WEBFLEET_USERNAME=Pavlo Manko
WEBFLEET_PASSWORD=Oldpass122!
WEBFLEET_ACCOUNT=maintenance-823
WEBFLEET_API_KEY=20a01522-1eac-4b56-96de-748bbe9c4083

MICROSOFT_CLIENT_ID=1e9f5d0e-e226-4076-aa96-8ca708611437
MICROSOFT_TENANT_ID=93ce9c27-3bb2-4ef2-b686-1829de4f2584
MICROSOFT_CLIENT_SECRET=70O8Q~Oi-GeF0V0djFUHIORPqo9vfkskEdkIrbt3

BACKEND_URL=http://localhost:8002
FRONTEND_URL=http://localhost:5174
```

## 🌐 API Endpoints

All centralized in `src/config/api.ts`

| Endpoint | Purpose |
|----------|---------|
| `/api/auth/microsoft` | Microsoft OAuth login |
| `/api/auth/callback/microsoft` | OAuth callback handler |
| `/api/dashboard/vehicle-summary` | KPI counts |
| `/api/dashboard/vehicles-by-status/:status` | Filter vehicles |
| `/api/drivers/excel` | Webfleet driver scores |
| `/api/chat/send` | Groq AI chatbot |

## 📊 Dashboard Features

- **KPI Cards**: Total, Allocated, Garage, Service Due, Spare, Reserved, Written Off
- **Charts**: Trade groups, vehicle types, spare vehicles, leavers
- **Data Sheet**: Detailed vehicle information
- **Webfleet Integration**: Driver performance scores
- **Chatbot**: Ask questions about fleet data (Groq AI)

## 🐛 Troubleshooting

### Port Already in Use
Ports dynamically change if in use:
- Backend tries: 8002, 8001, 8000
- Frontend tries: 5174, 5173, 5172

Update `.env.local` with the actual port shown in logs.

### OAuth Not Working
Check these in `backend/.env`:
- MICROSOFT_CLIENT_ID
- MICROSOFT_TENANT_ID  
- MICROSOFT_CLIENT_SECRET
- BACKEND_URL matches the server URL
- FRONTEND_URL matches where frontend is running

### Salesforce Not Connecting
The system automatically falls back to mock data if:
- Credentials are missing/invalid
- Salesforce is unavailable

Check `backend/.env` credentials are correct.

## 📁 Project Structure

```
fleet-health-monitor/
├── src/
│   ├── pages/
│   │   ├── Login.tsx (OAuth flow)
│   │   ├── FleetDashboard.tsx (Main KPIs)
│   │   ├── webfleet.tsx (Driver scores)
│   │   └── chatbot.tsx (Groq AI)
│   ├── config/
│   │   └── api.ts (Centralized endpoints)
│   └── App.tsx (Protected routing)
├── backend/
│   ├── routes/
│   │   ├── auth.py (OAuth handler)
│   │   ├── dashboard.py (KPI queries)
│   │   ├── webfleet.py (Driver data)
│   │   └── chat.py (Groq integration)
│   ├── app.py (FastAPI)
│   ├── salesforce_service.py
│   ├── webfleet_api.py
│   ├── groq_service.py
│   └── .env (Credentials)
└── .env.local (Frontend config)
```

## 🎯 What's Next?

1. ✅ Authentication working
2. ✅ Salesforce KPIs loading
3. ✅ Webfleet driver scores
4. ✅ AI chatbot ready
5. → Deploy to production (update URLs in .env)

## 📞 Support

For issues:
1. Check terminal output for error messages
2. Verify all credentials in `backend/.env`
3. Ensure backend and frontend are running
4. Check ports are correct in `.env.local`

---

**Built with**: React + TypeScript + FastAPI + Salesforce + Webfleet + Groq AI

Last Updated: January 29, 2026
