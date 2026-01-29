# Fleet Health Monitor - Complete Setup Guide

## 🚀 Quick Start

This guide walks you through setting up the complete Fleet Health Monitor application with:
- ✅ Microsoft Entra ID Authentication
- ✅ Fleet Dashboard with vehicle statistics
- ✅ AI Chatbot for fleet queries
- ✅ Vehicle upload and management
- ✅ Assets gallery
- ✅ Webfleet integration

---

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Salesforce account with custom Vehicle__c object
- Microsoft Entra ID (Optional, for OAuth)
- Groq API key (Optional, for AI chatbot)

---

## 🔧 Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.template` to `.env`:
```bash
cp .env.template .env
```

Edit `.env` with your credentials:

```
# Salesforce Configuration
SF_USERNAME=your_email@company.com
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_security_token
SF_DOMAIN=login  # or 'test' for sandbox

# Microsoft OAuth (For authentication)
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=common

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Groq API (Optional, for AI chatbot)
GROQ_API_KEY=your_groq_api_key

# Server
PORT=8000
```

### 3. Test Salesforce Connection

```bash
python -c "from salesforce_service import SalesforceService; sf = SalesforceService(); print('✅ Connected!')"
```

### 4. Start Backend Server

```bash
python app.py
```

Should see:
```
✅ Connected to Salesforce
✅ Groq Chat service initialized
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## 🎨 Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Access at: `http://localhost:5173`

---

## 🔐 Authentication Flow

### Microsoft Entra ID Setup

1. **Register Application in Azure Portal**
   - Go to Azure Portal → Entra ID → App registrations
   - Click "New registration"
   - Name: "Fleet Health Monitor"
   - Redirect URI: `http://localhost:8000/api/auth/callback/microsoft`
   - Click Register

2. **Configure Credentials**
   - Go to "Certificates & secrets"
   - Create new client secret
   - Copy: Client ID and Secret to `.env`

3. **Configure API Permissions**
   - Click "API permissions"
   - Add: User.Read
   - Grant admin consent

### Login Experience

1. User navigates to app (redirected to `/login`)
2. Clicks "Sign in with Microsoft"
3. Backend redirects to Microsoft OAuth
4. After authentication, user redirected to Dashboard
5. Session stored in sessionStorage

### Demo Login

For testing without Microsoft setup:
- Click "Demo Login" on login page
- Uses demo credentials (does not require setup)

---

## 📱 Application Routes

```
/login                    → Authentication page
/                         → Dashboard (protected)
/fleet-dashboard          → Fleet Dashboard (alias for /)
/upload                   → Vehicle upload
/assets                   → Assets gallery
/assets/:id              → Asset details
/webfleet                → Webfleet integration
/chatbot                 → AI chatbot interface
```

---

## 🤖 AI Chatbot Features

The chatbot uses Groq AI with few-shot prompting to:
- Answer questions about vehicle fleet
- Retrieve live Salesforce data
- Analyze driver history
- Provide maintenance insights

### Example Queries

```
- "How many vehicles are there?"
- "Tell me about VEH-439"
- "Who is driving that vehicle?"
- "Show spare vehicles"
- "List all drivers"
- "What vehicles need maintenance?"
```

### Chatbot Intent Classification

The AI classifies user intent into:
- count_all_vehicles
- get_vehicle_info
- get_vehicle_driver
- get_spare_vehicles
- get_maintenance_schedule
- And more...

---

## 📊 Dashboard

### Statistics Cards

- **Total Vehicles** - All vehicles in system
- **Allocated** - Currently assigned vehicles
- **In Garage** - Under maintenance
- **Due for Service** - Upcoming service dates
- **Spare Ready** - Available vehicles
- **Reserved** - Reserved vehicles
- **Written Off** - Decommissioned vehicles

### Features

- Click any card to filter assets by status
- Real-time data from Salesforce
- Refresh data automatically
- AI Chat button in header

---

## 📤 Vehicle Upload

1. Navigate to `/upload`
2. Enter vehicle details:
   - Van Number
   - Registration Number
   - Tracking Number
3. Optionally attach vehicle photo
4. Click "Search" to verify vehicle exists
5. Click "Save Asset" to create/update

---

## 🎯 Assets Gallery

1. Navigate to `/assets`
2. View all uploaded vehicles
3. Filter by status using dashboard cards
4. Click vehicle to see details
5. View registration, tracking, and photos

---

## 🔍 Troubleshooting

### Backend Issues

**Error: "No such column 'Description__c'"**
- Ensure custom Salesforce fields use `__c` suffix
- Check SOQL queries in `salesforce_service.py`

**Error: "Malformed request"**
- Invalid field names in Salesforce
- Check field exists in Vehicle__c object
- Verify field names have `__c` suffix

**Connection Error**
- Check `.env` credentials
- Verify Salesforce credentials are correct
- Test: `python -c "from salesforce_service import SalesforceService; SalesforceService()"`

### Frontend Issues

**Blank login page**
- Check backend is running: `http://localhost:8000/api/health`
- Verify CORS is enabled in FastAPI
- Check browser console for errors

**Chatbot not working**
- Verify Groq API key in `.env`
- Check backend: `http://localhost:8000/api/chat/health`
- Ensure Salesforce connection is active

**Assets not loading**
- Check `/api/assets/all` endpoint
- Verify Salesforce data exists
- Check backend logs for SOQL errors

---

## 🚀 Deployment

### Production Environment

1. **Backend (FastAPI)**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Frontend (React)**
   ```bash
   npm run build
   # Deploy dist/ folder to static hosting
   ```

3. **Environment Variables**
   - Set all `.env` variables in deployment platform
   - Use secure secrets management
   - Never commit `.env` file

### Azure Deployment Example

```bash
# Backend (Azure App Service)
az webapp create --resource-group myGroup --plan myPlan --name myApp --runtime "python:3.11"

# Frontend (Azure Static Web Apps)
az staticwebapp create --name myApp --source ./dist
```

---

## 📞 Support

For issues:
1. Check backend logs: `python app.py`
2. Check browser console (F12)
3. Verify all `.env` variables
4. Check Salesforce data exists
5. Review API endpoints at `/docs` (FastAPI auto-docs)

---

## 📝 Notes

- Sessions expire after 24 hours
- All vehicle data is live from Salesforce
- Chatbot requires active Groq API key
- Microsoft auth requires internet connection
- Demo login available without setup
