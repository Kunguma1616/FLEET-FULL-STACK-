# IMMEDIATE ACTION: Fix Your Upload Error

## THE ERROR
```
Unexpected token '<', "<!doctype "... is not valid JSON
```

## THE FIX (30 seconds)

### For Windows Users (Easiest)
1. Go to your project folder
2. Double-click: **`START_SERVERS.bat`**
3. Two terminal windows will open
4. Wait 5 seconds for them to start
5. Open browser: **`http://localhost:5173`**
6. Try upload again - should work!

### For Mac/Linux or Manual Start

**Terminal 1:**
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
Wait for: `Application startup complete`

**Terminal 2:**
```bash
npm run dev
```
Wait for: `Local: http://localhost:5173`

Then open browser to `http://localhost:5173`

## WHAT CHANGED
✅ Vite proxy configuration added - fixes communication between frontend and backend  
✅ Backend error handling improved - shows real errors instead of generic ones  
✅ Van number input sanitized - prevents SQL errors  

## THE WORKFLOW NOW

1. Click green **"Upload Vehicle"** button from home/dashboard
2. Upload an image
3. Enter a van number (like `VEH-00001`)
4. Click **"Search"**
5. Page will show:
   - Registration number ← From Salesforce
   - Tracking number ← From Salesforce  
   - Vehicle type ← From Salesforce
   - Driver history ← From Salesforce
6. Click **"Save as Asset"**
7. Redirected to portfolio to see your uploaded vehicle

## TEST WITHOUT UPLOAD
Go to: `http://localhost:8000/docs`

This is the API documentation. You can test the vehicle lookup directly:
1. Click `GET /api/vehicles/lookup/{van_number}`
2. Click "Try it out"
3. Type: `VEH-00001`
4. Click "Execute"
5. See JSON response below
6. If you see JSON → backend works ✅

## COMMON ISSUES

### Error Still Shows
- [ ] Did you double-click `START_SERVERS.bat`? OR
- [ ] Did you run both commands in separate terminals?
- [ ] Check browser console (F12) for actual error

### "Port 8000 in use"
Kill old process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux  
lsof -ti:8000 | xargs kill -9
```

### "Cannot find npm"
Make sure you're in project root, not backend folder

### Refresh not helping
- Close browser tab completely
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

## SUCCESS INDICATORS

You'll know it's working when:
1. You see `http://localhost:8000` in one terminal with `Uvicorn running`
2. You see `Local: http://localhost:5173` in another terminal
3. Upload page loads
4. Van number search returns data (no error)
5. Reg number field populates automatically
6. Tracking number field populates automatically

## FILES PROVIDED
- `START_SERVERS.bat` - One-click startup (Windows)
- `BACKEND_SETUP.md` - Detailed setup guide
- `ERROR_FIX_EXPLANATION.md` - Technical details about what was wrong

## NEXT STEPS

After fixing:
1. Upload vehicle image
2. Enter van number
3. All fields auto-fill
4. Click "Save as Asset"
5. View in "Asset Portfolio" page
6. See full vehicle details with driver history

That's it! The upload workflow should now be fully functional.

---

Still having issues? Check `BACKEND_SETUP.md` for comprehensive troubleshooting.
