# Microsoft Authentication & Chat Bot Setup Guide

## Overview
This application now includes:
- ✅ Microsoft Entra ID (Azure AD) Authentication
- ✅ Fleet AI Chat Bot with Salesforce integration
- ✅ Protected routes (requires authentication)
- ✅ Session management
- ✅ Real-time chat with intent classification using Groq AI

## Prerequisites

### 1. Microsoft Azure Setup
You need to register your application in Azure to enable Microsoft authentication.

#### Steps:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Enter Application name: `Fleet Health Monitor`
5. Select "Accounts in this organizational directory only"
6. Click Register

#### Configure Credentials:
1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Set expiration to "24 months"
4. Copy the secret value

#### Configure Redirect URI:
1. Go to "Authentication"
2. Add Platform → "Web"
3. Redirect URI: `http://localhost:8000/api/auth/callback/microsoft`
4. Check "Access tokens" and "ID tokens"
5. Click Save

### 2. Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Microsoft OAuth Configuration
MICROSOFT_CLIENT_ID=your_client_id_here
MICROSOFT_CLIENT_SECRET=your_client_secret_here
MICROSOFT_TENANT_ID=common

# Backend URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Salesforce Configuration
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_security_token
SF_DOMAIN=login

# Groq AI Configuration (Optional)
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Required Python Packages

Install all requirements:
```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- `fastapi` - Web framework
- `simple-salesforce` - Salesforce API
- `groq` - AI chat completions
- `python-dotenv` - Environment management
- `requests` - HTTP client for OAuth

## Running the Application

### 1. Start the Backend Server

```bash
cd backend
python app.py
```

Expected output:
```
✅ Groq service initialized
✅ Connected to Salesforce
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start the Frontend

```bash
# In a new terminal
npm run dev
```

Frontend will be at: `http://localhost:5173`

### 3. Access the Application

1. Navigate to `http://localhost:5173`
2. You'll be redirected to `/chatbot`
3. Click "Sign in with Microsoft"
4. After authentication, you'll be redirected back with a session
5. Start chatting!

## API Endpoints

### Authentication Endpoints
- `GET /api/auth/microsoft` - Initiates Microsoft OAuth login
- `GET /api/auth/callback/microsoft` - OAuth callback endpoint
- `GET /api/auth/session/{session_id}` - Get session info
- `POST /api/auth/logout/{session_id}` - Logout user
- `GET /api/auth/verify/{session_id}` - Verify session

### Chat Endpoints
- `POST /api/chat` - Send chat message
  ```json
  {
    "message": "How many vehicles?",
    "history": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]
  }
  ```
- `GET /api/chat/health` - Health check

## Features

### 1. Microsoft Authentication
- Secure OAuth 2.0 flow
- Session management with expiration
- User profile retrieval from Microsoft Graph

### 2. Chat Bot Features
- Intent classification using Groq AI's few-shot learning
- Live Salesforce data integration
- Conversation history tracking
- Smart message type detection (success, alert, info)
- Copy message functionality
- Session management

### 3. Chat Examples
Try asking:
- "How many vehicles are there in total?"
- "How many allocated vehicles?"
- "Show me spare vehicles"
- "List all drivers"
- "What vehicles need maintenance?"
- "Tell me about VEH-439"
- "Show me the costs for this vehicle"

### 4. Message Types
Messages are automatically categorized:
- **Info** (Blue) - General information
- **Success** (Green) - Confirmations and completed actions
- **Alert** (Red) - Warnings, errors, and issues

## Troubleshooting

### Issue: "Not authenticated"
- Ensure you've signed in with Microsoft
- Check that `MICROSOFT_CLIENT_ID` and `MICROSOFT_CLIENT_SECRET` are set correctly
- Verify redirect URI matches in Azure portal

### Issue: Chat not responding
- Check backend is running: `http://localhost:8000/api/chat/health`
- Ensure `GROQ_API_KEY` is set for AI features
- Check Salesforce connection in backend logs

### Issue: Microsoft login fails
- Verify `MICROSOFT_TENANT_ID` is correct
- Check redirect URI: `http://localhost:8000/api/auth/callback/microsoft`
- Ensure application is registered in Azure AD

### Issue: Protected routes redirect to chatbot
- User session has expired (24-hour expiration)
- Session data was cleared from storage
- Sign in again with Microsoft

## Architecture

```
┌─────────────────────────────────────────┐
│         React Frontend (Vite)           │
│         - Chatbot Component             │
│         - Session Management           │
│         - Protected Routes              │
└──────────────┬──────────────────────────┘
               │
               ├── /api/auth/microsoft ───┐
               │                           │
               ├── /api/auth/callback ────┤─→ Microsoft OAuth
               │                           │   (Azure AD)
               ├── /api/chat ─────┐        │
               │                   │        │
               └───────────────────┼────────┘
                                   │
                    ┌──────────────▼────────────┐
                    │  FastAPI Backend         │
                    │  - Session Management    │
                    │  - Chat Router           │
                    │  - Auth Router           │
                    └──────────────┬────────────┘
                                   │
                    ┌──────────────┴────────────┐
                    │                           │
                  ┌─▼──────────┐      ┌──────────▼──┐
                  │ Groq AI    │      │ Salesforce  │
                  │ (Chat)     │      │ (Data)      │
                  └────────────┘      └─────────────┘
```

## Files Modified/Created

### Backend Files
- `/api/auth/routes.py` - Microsoft OAuth and session management
- `/api/chat/routes.py` - Chat endpoint and intent classification
- `groq_service.py` - AI intent classification and response generation
- `app.py` - Updated to include auth and chat routers

### Frontend Files
- `src/App.tsx` - Added protected routes and chatbot route
- `src/pages/chatbot.tsx` - Complete chat application
- `src/pages/Dashboard.tsx` - Added "Chat with AI" button

## Security Notes

1. **Session Management**
   - Sessions stored in memory (use Redis for production)
   - 24-hour expiration
   - Uses secure tokens (secrets.token_urlsafe)

2. **OAuth Flow**
   - Uses authorization code flow
   - Client secret never exposed to frontend
   - State parameter should be added for production

3. **API Protection**
   - Chat and data endpoints are protected via session verification
   - Frontend enforces authentication with ProtectedRoute component

## Next Steps

1. ✅ Configure Microsoft Entra ID in Azure
2. ✅ Set up environment variables
3. ✅ Install Python dependencies
4. ✅ Start backend server
5. ✅ Start frontend server
6. ✅ Access at `http://localhost:5173`

## Support

For issues or questions:
1. Check backend logs: `python app.py`
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure Salesforce connection is working
5. Test API endpoints with curl or Postman
