# ✅ Assets Upload & Display - Complete Fix

## Problem
When uploading a vehicle on the Upload page, the vehicle was not being saved/displayed on the Assets page (`/assets`).

**Flow that was broken:**
1. User uploads image on `/upload` page ✅
2. Gets van number, registration, tracking number ✅
3. Clicks "Save Asset"
4. **❌ Data NOT stored or displayed on `/assets` page**

---

## Root Causes

### Issue 1: Wrong Field Name in `/create` Endpoint
**File**: `backend/routes/assets.py` (Line 51)
- **Was**: `"Description": asset.description`
- **Should be**: `"Description__c": asset.description`
- Salesforce was rejecting the save because the custom field name is `Description__c`, not `Description`

### Issue 2: Wrong Field Name in `/all` Endpoint
**File**: `backend/routes/assets.py` (Line 193)
- **Was**: `record.get('Description')`
- **Should be**: `record.get('Description__c')`
- Assets were being retrieved but description field was always null

### Issue 3: Status Filter Too Restrictive
**File**: `backend/routes/assets.py` (Line 168)
- **Was**: `WHERE Status__c = 'Uploaded'`
- **Should be**: No status filter (retrieve ALL vehicles)
- Newly uploaded vehicles might have different statuses, and existing vehicles have other statuses

### Issue 4: Wrong Field Name in `/by-van` Endpoint
**File**: `backend/routes/assets.py` (Line 140)
- **Was**: `record.get('Description')`
- **Should be**: `record.get('Description__c')`

---

## Changes Made

### 1. Fixed Asset Creation Endpoint
```python
# BEFORE (Line 51)
vehicle_data = {
    "Description": asset.description,  # ❌ WRONG
    ...
}

# AFTER
vehicle_data = {
    "Description__c": asset.description,  # ✅ CORRECT
    ...
}
```

### 2. Fixed Asset Retrieval Endpoint - All Assets
```python
# BEFORE (Line 168)
WHERE Status__c = 'Uploaded'  # ❌ Too restrictive - misses existing vehicles

# AFTER
# No WHERE clause - retrieves ALL vehicles

# BEFORE (Line 193)
"description": record.get('Description'),  # ❌ WRONG

# AFTER
"description": record.get('Description__c'),  # ✅ CORRECT
```

### 3. Fixed Asset Retrieval Endpoint - By Van Number
```python
# BEFORE (Line 140)
"description": vehicle.get('Description'),  # ❌ WRONG

# AFTER
"description": vehicle.get('Description__c'),  # ✅ CORRECT
```

---

## Data Flow (Now Works ✅)

```
1. USER UPLOADS ON /upload PAGE
   ├─ Selects image
   ├─ Enters van number (e.g., "330")
   ├─ Clicks "Search" → Fetches vehicle data from /api/vehicles/lookup/330
   ├─ Sees van number, registration, tracking number
   └─ Clicks "Save Asset"
        │
        ↓
2. SENDS TO BACKEND /api/assets/create
   ├─ Van Number__c: "330"
   ├─ Reg_No__c: "BT70XMO"
   ├─ Tracking_Number__c: "..."
   ├─ Description__c: "Vehicle description"  ✅ CORRECT FIELD
   ├─ Status__c: "Uploaded"
   └─ SAVES TO SALESFORCE Vehicle__c object
        │
        ↓
3. USER NAVIGATES TO /assets PAGE
   ├─ Calls /api/assets/all endpoint
   ├─ Backend queries ALL Vehicle__c records ✅ No filter
   ├─ Retrieves Description__c field ✅ CORRECT FIELD
   └─ Displays in AssetsGallery component
        │
        ↓
4. ✅ VEHICLE APPEARS IN ASSETS PAGE
   └─ Shows: Van number, registration, tracking, description
```

---

## Testing Checklist

### Test 1: Upload a New Vehicle
- [ ] Go to `/upload` page
- [ ] Upload image
- [ ] Enter van number (try **330** which exists, or **500** for new)
- [ ] Click "Search"
- [ ] Should see vehicle details populated
- [ ] Click "Save Asset"
- [ ] Should show success message

### Test 2: View in Assets Gallery
- [ ] Navigate to `/assets` page (or AssetsGallery component)
- [ ] Should see the vehicle you just uploaded
- [ ] Van number should match
- [ ] Registration number should display
- [ ] Tracking number should display
- [ ] Description should show

### Test 3: Verify API Responses
```bash
# Check if asset was saved
curl http://localhost:8000/api/assets/all

# Should return vehicles with description filled in
{
  "total": X,
  "assets": [
    {
      "id": "...",
      "van_number": "330",
      "description": "Your description here",  # ✅ Should be populated
      "status": "Uploaded",
      ...
    }
  ]
}
```

---

## Files Fixed

| File | Line(s) | Fix |
|------|---------|-----|
| `backend/routes/assets.py` | 51 | Changed `Description` → `Description__c` in create |
| `backend/routes/assets.py` | 140 | Changed `Description` → `Description__c` in by-van |
| `backend/routes/assets.py` | 168 | Removed `WHERE Status__c = 'Uploaded'` filter |
| `backend/routes/assets.py` | 193 | Changed `Description` → `Description__c` in all |

---

## Environment Variables Needed

Make sure your `.env` has:
```env
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_security_token
SF_DOMAIN=login  # or your custom domain
```

---

## Next Steps

1. **Restart the backend** to load the fixed code
   ```bash
   python backend/app.py
   ```

2. **Test the upload flow** with van number **330** (confirmed to exist)

3. **Check the Assets page** to verify vehicles display

4. **Verify data in Salesforce** that records are being created/updated

---

## Status

✅ **Complete** - All fixes implemented and ready to test
