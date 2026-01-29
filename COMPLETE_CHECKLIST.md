# ✅ COMPLETE SETUP CHECKLIST

## 🚀 Getting Started - Step by Step

### Phase 1: Prerequisites ✅
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] Salesforce account with Vehicle__c object
- [ ] Microsoft Azure account (optional, for OAuth)

---

### Phase 2: Backend Configuration ⚙️

#### 2.1 Environment Setup
- [ ] Open `backend/.env.template`
- [ ] Copy to `backend/.env`
- [ ] Fill in Salesforce credentials:
  ```
  SF_USERNAME=your_email@company.com
  SF_PASSWORD=your_password
  SF_SECURITY_TOKEN=your_token
  SF_DOMAIN=login  # or 'test' for sandbox
  ```
- [ ] Fill in Microsoft OAuth (optional):
  ```
  MICROSOFT_CLIENT_ID=your_client_id
  MICROSOFT_CLIENT_SECRET=your_secret
  MICROSOFT_TENANT_ID=common
  ```

#### 2.2 Python Setup
- [ ] Navigate to backend: `cd backend`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify Salesforce connection:
  ```bash
  python -c "from salesforce_service import SalesforceService; SalesforceService(); print('✅ Connected')"
  ```

#### 2.3 Start Backend
- [ ] Run: `python app.py`
- [ ] Verify output shows:
  - ✅ Connected to Salesforce
  - ✅ Groq Chat service initialized
  - INFO: Uvicorn running on http://0.0.0.0:8000

---

### Phase 3: Frontend Configuration 🎨

#### 3.1 Node Modules Setup
- [ ] Return to root directory: `cd ..`
- [ ] Install npm packages: `npm install`
- [ ] Verify node_modules created

#### 3.2 Start Frontend
- [ ] Run: `npm run dev`
- [ ] Verify output shows:
  - VITE v4.x.x ready in XXX ms
  - ➜ Local: http://localhost:5173/

---

### Phase 4: Application Testing 🧪

#### 4.1 Login Testing
- [ ] Open browser: http://localhost:5173
- [ ] See login page
- [ ] Click "Demo Login"
- [ ] Should redirect to Dashboard
- [ ] Check sessionStorage in DevTools (F12 → Application → Storage)

#### 4.2 Dashboard Testing
- [ ] See 7 stat cards with numbers
- [ ] Numbers match Salesforce data
- [ ] Click on a stat card
- [ ] Should filter /assets by status

#### 4.3 Chatbot Testing
- [ ] Click "AI Chat" button in header
- [ ] See chatbot interface
- [ ] Click quick question buttons
- [ ] Chat should respond with data
- [ ] Create new chat session
- [ ] Verify message history persists

#### 4.4 Upload Testing
- [ ] Click "Upload Vehicles" in sidebar
- [ ] Enter vehicle details
- [ ] Click "Search" to verify
- [ ] Attach photo (optional)
- [ ] Click "Save Asset"
- [ ] Check /assets to see new vehicle

#### 4.5 Navigation Testing
- [ ] Click all sidebar items
- [ ] Active highlighting works
- [ ] Responsive on mobile
- [ ] Click "Sign Out"
- [ ] Redirected to /login
- [ ] sessionStorage cleared

---

### Phase 5: Microsoft OAuth Setup (Optional) 🔐

#### 5.1 Azure Portal Configuration
- [ ] Log into Azure Portal (portal.azure.com)
- [ ] Go to Entra ID → App registrations
- [ ] Click "New registration"
- [ ] Name: "Fleet Health Monitor"
- [ ] Redirect URI: `http://localhost:8000/api/auth/callback/microsoft`
- [ ] Click Register

#### 5.2 Configure Credentials
- [ ] Go to "Certificates & secrets"
- [ ] Create new client secret
- [ ] Copy: Value (this is CLIENT_SECRET)
- [ ] Go back to Overview
- [ ] Copy: Application (client) ID
- [ ] Add to backend/.env:
  ```
  MICROSOFT_CLIENT_ID=<copied application id>
  MICROSOFT_CLIENT_SECRET=<copied secret>
  ```

#### 5.3 Configure Permissions
- [ ] Click "API permissions"
- [ ] Add permission → Microsoft Graph
- [ ] Click "User.Read"
- [ ] Grant admin consent

#### 5.4 Test OAuth Login
- [ ] Restart backend: `python app.py`
- [ ] Go to login page
- [ ] Click "Sign in with Microsoft"
- [ ] Should redirect to Microsoft login
- [ ] After authentication, redirected to Dashboard

---

### Phase 6: Groq AI Setup (Optional) 🤖

#### 6.1 Get Groq API Key
- [ ] Visit: https://console.groq.com
- [ ] Sign up or login
- [ ] Create API key
- [ ] Copy the key

#### 6.2 Configure Groq
- [ ] Add to backend/.env:
  ```
  GROQ_API_KEY=gsk_xxxxxx
  ```
- [ ] Restart backend

#### 6.3 Test Chatbot
- [ ] Login to app
- [ ] Click "AI Chat"
- [ ] Ask question: "How many vehicles?"
- [ ] Should get response powered by Groq AI

---

### Phase 7: Deployment Preparation 🚀

#### 7.1 Frontend Build
- [ ] Run: `npm run build`
- [ ] Verify `dist/` folder created
- [ ] Ready to deploy to:
  - Vercel
  - Netlify
  - Azure Static Web Apps
  - AWS S3 + CloudFront

#### 7.2 Backend Containerization
- [ ] Create `Dockerfile` in backend:
  ```dockerfile
  FROM python:3.11
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
  ```
- [ ] Build: `docker build -t fleet-api .`
- [ ] Ready for deployment to Docker Hub, AWS ECR, etc.

#### 7.3 Environment Variables for Production
- [ ] Set in deployment platform:
  ```
  SF_USERNAME
  SF_PASSWORD
  SF_SECURITY_TOKEN
  SF_DOMAIN
  MICROSOFT_CLIENT_ID
  MICROSOFT_CLIENT_SECRET
  MICROSOFT_TENANT_ID
  FRONTEND_URL
  BACKEND_URL
  GROQ_API_KEY (optional)
  PORT
  ```

---

### Phase 8: Verification Checklist ✅

#### Functionality
- [ ] Login works (Demo or Microsoft)
- [ ] Dashboard shows statistics
- [ ] All stat cards display data
- [ ] Click card filters assets
- [ ] Chatbot responds to questions
- [ ] Can upload vehicles
- [ ] Assets gallery shows vehicles
- [ ] Navigation works
- [ ] Sign out clears session
- [ ] Protected routes require auth

#### Performance
- [ ] Dashboard loads in < 2 seconds
- [ ] Chatbot responds in < 3 seconds
- [ ] Page transitions are smooth
- [ ] No console errors
- [ ] Responsive on mobile

#### Data
- [ ] Salesforce connection active
- [ ] Statistics match Salesforce
- [ ] Vehicles display correctly
- [ ] Photos upload successfully
- [ ] Chatbot queries return accurate data

#### UI/UX
- [ ] All colors displaying correctly
- [ ] Icons showing properly
- [ ] Text readable
- [ ] Buttons clickable
- [ ] Mobile layout responsive
- [ ] Empty states show guidance

---

### Phase 9: Documentation Review 📚

- [ ] Read README_MAIN.md
- [ ] Review SETUP_COMPLETE.md
- [ ] Check IMPLEMENTATION_DONE.md
- [ ] Understand QUICK_SUMMARY.md
- [ ] Review API docs at /docs endpoint

---

### Phase 10: Troubleshooting Guide 🔧

#### Backend Won't Start
- [ ] Check Python version: `python --version` (should be 3.8+)
- [ ] Check dependencies: `pip list | grep fastapi`
- [ ] Check port: `lsof -i :8000` (Windows: `netstat -ano | findstr :8000`)
- [ ] Check .env file exists and is readable
- [ ] Check Salesforce credentials are correct

#### Frontend Won't Load
- [ ] Check Node.js version: `node --version` (should be 16+)
- [ ] Check npm version: `npm --version`
- [ ] Clear npm cache: `npm cache clean --force`
- [ ] Delete node_modules: `rm -rf node_modules`
- [ ] Reinstall: `npm install`

#### Can't Connect to Salesforce
- [ ] Verify SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN
- [ ] Check IP whitelist in Salesforce (if applicable)
- [ ] Test credentials in Salesforce directly
- [ ] Check SF_DOMAIN setting (login vs test)
- [ ] Verify Vehicle__c object exists in Salesforce

#### Chatbot Not Responding
- [ ] Check GROQ_API_KEY is set (optional)
- [ ] If not set, chatbot still works with Salesforce queries
- [ ] Check backend logs for errors
- [ ] Verify Salesforce connection is active
- [ ] Test Groq API key validity

#### Microsoft OAuth Not Working
- [ ] Check MICROSOFT_CLIENT_ID is correct
- [ ] Check MICROSOFT_CLIENT_SECRET is correct
- [ ] Verify redirect URI matches exactly
- [ ] Check Microsoft app permissions (User.Read)
- [ ] Ensure admin consent was granted

---

### Phase 11: Performance Optimization 📈

- [ ] Enable gzip compression in production
- [ ] Use CDN for frontend assets
- [ ] Implement caching headers
- [ ] Minimize frontend bundle size
- [ ] Use database connection pooling (Salesforce)
- [ ] Implement rate limiting on API

---

### Phase 12: Security Hardening 🔒

- [ ] Never commit .env file to Git
- [ ] Use strong Salesforce password
- [ ] Rotate API keys regularly
- [ ] Use HTTPS in production
- [ ] Implement CORS policies
- [ ] Add request validation
- [ ] Implement rate limiting
- [ ] Use environment-specific secrets

---

## 📝 Success Criteria

### ✅ Backend Ready
- Salesforce connected
- API endpoints responding
- Chatbot initialized
- No startup errors

### ✅ Frontend Ready
- Page loads quickly
- All routes accessible
- Navigation works
- Data displays correctly

### ✅ Authentication Ready
- Demo login works
- Microsoft OAuth configured
- Sessions persist
- Protected routes enforced

### ✅ Features Ready
- Dashboard statistics display
- Chatbot responds
- Upload works
- Assets display
- Navigation functions

---

## 🎉 You're Done!

Once all checkboxes are marked, your Fleet Health Monitor application is:
- ✅ Fully configured
- ✅ Properly tested
- ✅ Ready for production
- ✅ Optimized for performance
- ✅ Secured appropriately

**Congratulations! 🚗✨**
