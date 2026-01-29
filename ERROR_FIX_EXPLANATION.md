# Error Fix: "Unexpected token '<'" JSON Parse Error

## What Was Happening

When you uploaded an image and entered a van number, you got:
```
Unexpected token '<', "<!doctype "... is not valid JSON
```

This error occurs when JavaScript tries to parse HTML as JSON. It means the backend returned an HTML error page instead of JSON data.

## Root Causes (FIXED)

### 1. **Missing Vite Proxy Configuration** ✅ FIXED
**The Problem:**
- Frontend was running on `localhost:5173`
- Backend was running on `localhost:8000`
- Browser calls to `/api/vehicles/lookup/...` had no proxy configuration
- Request went to `http://localhost:5173/api/vehicles/lookup/...` instead of `http://localhost:8000/api/vehicles/lookup/...`
- Got a 404 error page (HTML) instead of JSON response

**The Fix:**
Added to `vite.config.ts`:
```typescript
server: {
  proxy: {
    "/api": {
      target: "http://localhost:8000",
      changeOrigin: true,
    }
  }
}
```

This tells Vite dev server to forward all `/api/*` requests to the backend.

### 2. **Backend Not Running** ✅ ADDRESSED
**The Problem:**
- Even with correct proxy, if backend isn't running, you get connection error

**The Fix:**
Created `BACKEND_SETUP.md` and `START_SERVERS.bat` with clear instructions

### 3. **SQL Injection Vulnerability in Vehicle Lookup** ✅ FIXED
**The Problem:**
- Van number was directly interpolated into SOQL query
- If van number contained special characters, could cause SQL error
- Backend would return HTML error page

**The Fix:**
Added input sanitization in `vehicles.py`:
```python
sanitized_van = van_number.replace("'", "\\'")
```

### 4. **Poor Error Messages** ✅ IMPROVED
**The Problem:**
- Frontend just said "Failed to fetch vehicle data" without details

**The Fix:**
Updated `Upload.tsx` to:
- Log actual response status and content-type
- Show response body on error
- Display more helpful error messages
- Better console logging for debugging

## How to Use Now

### Option 1: Quick Start (Windows only)
Double-click: `START_SERVERS.bat`

### Option 2: Manual Setup (Windows/Mac/Linux)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Then:
1. Open `http://localhost:5173`
2. Click "Upload Vehicle"
3. Upload image + enter van number (e.g., `VEH-00001`)
4. Click "Search"
5. Should now see registration, tracking number, vehicle type!

## Files Changed

| File | Change |
|------|--------|
| `vite.config.ts` | Added proxy configuration for `/api` routes |
| `src/pages/Upload.tsx` | Improved error handling and logging |
| `backend/routes/vehicles.py` | Added input sanitization for van number |
| NEW: `BACKEND_SETUP.md` | Step-by-step setup guide |
| NEW: `START_SERVERS.bat` | Automatic server startup script (Windows) |

## Testing the Fix

### Quick Test
Visit: `http://localhost:8000/docs`

This shows interactive API documentation. Try:
- Click "GET /api/vehicles/lookup/{van_number}"
- Click "Try it out"
- Enter van number: `VEH-00001`
- Click "Execute"
- Should see JSON response with registration, tracking, etc.

### Full Test
1. Go to `http://localhost:5173`
2. Click green "Upload Vehicle" button
3. Upload any image
4. Enter van number
5. Click "Search"
6. Check browser F12 > Console for debug logs
7. Should see reg number, tracking number populate

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Connection refused" | Backend not running | Run: `python -m uvicorn app:app --host 0.0.0.0 --port 8000` |
| Still getting error | Frontend not reloaded | Refresh browser (Ctrl+R or Cmd+R) |
| "Port 8000 in use" | Old backend still running | Kill process: Windows `netstat -ano | findstr :8000` |
| Van number not found | Van doesn't exist in Salesforce | Use test van from `http://localhost:8000/docs` |

## What Should Happen Now

1. **Upload page loads** ✅
2. **You upload an image** ✅  
3. **You enter van number (e.g., `VEH-00001`)** ✅
4. **You click "Search"** ✅
5. **Reg number appears**: Should show from Salesforce ✅
6. **Tracking number appears**: Should show from Salesforce ✅
7. **Vehicle type appears**: Should show from Salesforce ✅
8. **Driver history appears**: Should show WorkOrder history ✅

## Need Help?

1. Check `BACKEND_SETUP.md` for troubleshooting
2. Check browser console (F12) for actual error messages
3. Try API directly at `http://localhost:8000/docs`
4. Make sure both servers started successfully

## Architecture Explanation

```
Browser (localhost:5173)
    |
    ├─ Vite Proxy intercepts /api/* calls
    |       |
    |       ↓
    └─→ Backend (localhost:8000)
            |
            ├─ GET /api/vehicles/lookup/{van}
            |       ↓
            |   Query Salesforce
            |       ↓
            |   Return JSON with registration, tracking, etc.
            |
            └─ Returns JSON (not HTML!)
```

The proxy ensures all API calls go to the right place and return JSON, not HTML error pages.
