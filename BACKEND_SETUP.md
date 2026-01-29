# QUICK FIX: Backend Server Setup

## Problem
You're getting "Unexpected token '<'" which means:
- Backend server is **NOT RUNNING**
- OR Frontend can't reach the backend

## Solution

### Step 1: Start the Backend Server

Open a **NEW terminal** in VS Code (don't use existing ones) and run:

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output** (should see):
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 2: Start the Frontend Server

In a **DIFFERENT terminal**, run:

```bash
npm run dev
```

**Expected output** (should see):
```
  VITE v... ready in ... ms
  ➜  Local:   http://localhost:5173/
```

### Step 3: Test the Upload Feature

1. Open `http://localhost:5173/` in your browser
2. Click **"Upload Vehicle"** button
3. Upload an image
4. Enter a van number (e.g., `VEH-00001`, `VEH-00002`)
5. Click **"Search"** button
6. Should now see:
   - Registration Number
   - Tracking Number
   - Vehicle Type
   - Driver History

### If Still Getting Error

Check the browser **Developer Console** (F12 > Console tab):
- Look for the actual error message
- Check Network tab to see if `/api/vehicles/lookup/...` is returning HTML or JSON

## What Was Fixed

1. **vite.config.ts**: Added proxy configuration so frontend calls to `/api/*` get routed to `http://localhost:8000`
2. **Upload.tsx**: Improved error handling and logging to show what's really happening
3. **vehicles.py**: Added input sanitization for van number

## Key Ports

- Frontend: **http://localhost:5173**
- Backend: **http://localhost:8000**
- Backend API Docs: **http://localhost:8000/docs** (try this to test endpoints directly!)

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Unexpected token '<'" | Backend not running. Run: `python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload` |
| "Port 8000 already in use" | Kill the old process: `lsof -ti:8000 \| xargs kill -9` (Mac/Linux) or `netstat -ano \| findstr :8000` (Windows) |
| "Cannot find module fastapi" | Run: `pip install -r requirements.txt` from the backend folder |
| Van number not found | Check the van number exists in Salesforce. Try in backend at: `http://localhost:8000/docs` |

## Testing API Directly

Visit: `http://localhost:8000/docs`

This shows all available API endpoints. You can test them directly here!

Try:
- GET `/api/vehicles/lookup/VEH-00001`
- GET `/api/vehicles/list`
- GET `/api/assets/all`
