# IMMEDIATE: Find Your Van Numbers

## The Issue
You tried van number "379" but it doesn't exist in Salesforce → 404 error

## The Fix (30 seconds)

### Step 1: See Available Vans
Visit: **`http://localhost:8000/docs`**

Click the dropdown arrow next to: **`GET /api/vehicles/list`**

Click blue button: **"Execute"**

Scroll down → See **ALL** available vehicles with van numbers

### Step 2: Copy a Van Number
From the response, copy any `van_number` value (like `VEH-00001`)

### Step 3: Try Upload Again
1. Go to `http://localhost:5173`
2. Click "Upload Vehicle" 
3. Upload an image
4. Paste the van number from Step 2
5. Click "Search"
6. Should see: Registration, Tracking, Type ✅

## Alternative: Auto-Suggestions
If you want the app to show suggestions automatically:
1. Type any van number
2. Click "Search"
3. If not found → App shows "Did you mean?" box below
4. Click a suggestion
5. Auto-fills and searches ✅

## That's It!

Once you use a valid van number from your Salesforce database, everything works!

---

**Not sure which vans you have?**

Visit: `http://localhost:8000/docs`
→ Click `GET /api/vehicles/list`
→ Execute
→ See all your vans at the bottom!
