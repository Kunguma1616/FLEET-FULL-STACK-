# 🚗 Vehicle Upload & Asset Management System - Complete Guide

## Quick Start

### 1️⃣ Upload a Vehicle

**URL**: `http://localhost:5173/upload`

**Steps**:
1. Click "Click to upload vehicle image" to add a photo
2. Enter van number in the "Van Number" field (e.g., `379`)
3. Click "Search" button
4. System automatically fetches:
   - ✅ Registration Number (e.g., `YB24UTN`)
   - ✅ Tracking Number (e.g., `WZ5043I00082`)
   - ✅ Vehicle Type (e.g., `Long wheel base high roof`)
   - ✅ Complete Driver History
4. Review all information
5. Click "Save as Asset" button
6. ✅ Vehicle is now stored and searchable

---

## 2️⃣ View All Uploaded Vehicles

**URL**: `http://localhost:5173/assets`

**Features**:
- 📊 Grid view showing all uploaded vehicles
- 🔎 Search bar - search by:
  - Van number
  - Registration number
  - Tracking number
  - Vehicle name
- 📋 Quick info cards with:
  - Vehicle image placeholder
  - Van number
  - Registration
  - Tracking number
  - Vehicle type
  - Upload date
  - Status badge

**Status Badges**:
- 🟢 Green: "Uploaded" (newly added)
- 🔵 Blue: "Allocated" (in use)
- ⚪ Gray: "Spare" (available)
- 🔴 Red: "Written Off" (retired)
- 🟣 Purple: "Reserved" (reserved)

---

## 3️⃣ View Detailed Asset Information

**URL**: `http://localhost:5173/assets/379` (van number)

**Displays**:

### 📦 Vehicle Information Cards
- **Van #**: 379
- **Registration**: YB24UTN
- **Tracking #**: WZ5043I00082
- **Type**: Long wheel base high roof

### 🖼️ Vehicle Image
- Full size vehicle image (if uploaded)
- Placeholder if no image

### 📝 Description
- Complete vehicle description
- Specifications and features

### 👥 Complete Driver History
- All driver assignments
- Usage history
- Maintenance records
- Service dates

### 🤖 AI Analysis Report
- Vehicle condition (Excellent/Good/Fair/Poor)
- Visible damage assessment
- Cleanliness evaluation
- Safety observations
- Maintenance recommendations
- Driver behavior impact

### 💾 Actions
- **Export**: Download vehicle details as PDF
- **Delete**: Remove vehicle from system

---

## 🔌 API Reference

### Vehicle Lookup API

```
GET /api/vehicles/lookup/{van_number}
```

**Example**:
```bash
curl http://localhost:8000/api/vehicles/lookup/379
```

**Response**:
```json
{
  "van_number": "379",
  "registration_number": "YB24UTN",
  "tracking_number": "WZ5043I00082",
  "vehicle_name": "Long wheel base high roof",
  "vehicle_type": "Van",
  "description": "Yellow, standard roof, side sliding doors, company livery",
  "status": "Allocated",
  "driver_history": "George Widdowson 10.02.25 1pm\nJohn Smith 09.02.25 9am",
  "driver_name": "George Widdowson",
  "vehicle_id": "a374G000002s87XQAQ"
}
```

---

### Asset Creation API

```
POST /api/assets/create
Content-Type: application/json
```

**Request Body**:
```json
{
  "van_number": "379",
  "registration_number": "YB24UTN",
  "tracking_number": "WZ5043I00082",
  "vehicle_name": "Long wheel base high roof",
  "driver_history": "Complete history text...",
  "vehicle_type": "Van",
  "description": "Yellow vehicle...",
  "ai_details": "AI analysis report...",
  "image_data": "base64_encoded_image_string"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Asset created successfully",
  "vehicle_id": "a374G000002s87XQAQ",
  "van_number": "379"
}
```

---

### Get All Assets API

```
GET /api/assets/all
```

**Response**:
```json
{
  "total": 1,
  "assets": [
    {
      "id": "a374G000002s87XQAQ",
      "name": "Long wheel base high roof",
      "van_number": "379",
      "registration_number": "YB24UTN",
      "tracking_number": "WZ5043I00082",
      "vehicle_type": "Van",
      "description": "Yellow vehicle...",
      "status": "Uploaded",
      "created_date": "2026-01-28T14:30:00Z"
    }
  ]
}
```

---

### AI Analysis API

```
POST /api/ai/extract-vehicle-details
Content-Type: multipart/form-data

Parameters:
- image: File (vehicle image)
- van_number: String (e.g., "379")
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/ai/extract-vehicle-details \
  -F "image=@vehicle.jpg" \
  -F "van_number=379"
```

**Response**:
```json
{
  "status": "success",
  "details": "📊 Vehicle Analysis Report - Van 379\n\n🚗 **Vehicle Condition**: Good\n   - Exterior: Well-maintained...",
  "van_number": "379"
}
```

---

## 🗂️ File Structure

```
fleet-health-monitor/
├── src/
│   ├── pages/
│   │   ├── Upload.tsx              ← Vehicle upload page
│   │   ├── AssetsGallery.tsx       ← Assets list view
│   │   ├── AssetDetail.tsx         ← Detailed asset view
│   │   └── ...other pages
│   ├── App.tsx                     ← Routes configuration
│   └── ...
├── backend/
│   ├── routes/
│   │   ├── vehicles.py             ← Vehicle lookup endpoints
│   │   ├── assets.py               ← Asset management endpoints
│   │   ├── ai.py                   ← AI analysis endpoints
│   │   └── ...other routes
│   ├── app.py                      ← FastAPI configuration
│   └── ...
├── IMPLEMENTATION_SUMMARY.md       ← Detailed implementation docs
└── SETUP_INSTRUCTIONS.sh           ← Setup guide
```

---

## 🧪 Testing Checklist

- [ ] Upload page loads at `/upload`
- [ ] Can upload an image
- [ ] Can enter van number
- [ ] Search fetches vehicle data from Salesforce
- [ ] All fields populate correctly
  - [ ] Registration number
  - [ ] Tracking number
  - [ ] Driver history
  - [ ] Vehicle type
- [ ] Can save as asset
- [ ] Asset appears in gallery at `/assets`
- [ ] Can search assets by van/reg/tracking
- [ ] Can click "View Full Details" to go to detail page
- [ ] Detail page shows all information
- [ ] AI analysis displays correctly
- [ ] Can export asset
- [ ] Can delete asset

---

## 🐛 Troubleshooting

### Issue: "Vehicle not found"
- ✅ Check van number is correct and exists in Salesforce
- ✅ Verify Salesforce connection is active
- ✅ Check SALESFORCE_* environment variables

### Issue: AI analysis not appearing
- ✅ ANTHROPIC_API_KEY may not be set
- ✅ System falls back to template if API unavailable
- ✅ Check console for API errors

### Issue: Image not saving
- ✅ Ensure image file size is reasonable (< 5MB)
- ✅ Check browser console for errors
- ✅ Verify API endpoint is accessible

### Issue: Search not working
- ✅ Search is case-insensitive
- ✅ Partial matches work (e.g., "37" finds "379")
- ✅ Check that assets are actually in database

---

## 📊 Example Workflow

### Scenario: Adding a new company vehicle

1. **Manager uploads vehicle photo** 📸
   - Navigate to `/upload`
   - Click image upload
   - Select vehicle photo

2. **Manager enters van number** 🔢
   - Enters: `379`
   - Clicks "Search"

3. **System auto-populates details** ⚡
   - Gets registration: `YB24UTN`
   - Gets tracking: `WZ5043I00082`
   - Gets driver history
   - Gets vehicle type: `Long wheel base high roof`

4. **AI analyzes vehicle image** 🤖
   - Assesses condition
   - Notes any damage
   - Safety check
   - Maintenance recommendations

5. **Manager saves asset** 💾
   - Clicks "Save as Asset"
   - Vehicle is now in system

6. **Other staff view asset** 👥
   - Go to `/assets`
   - Search for van `379`
   - Click "View Full Details"
   - See all information and AI analysis

---

## 🎨 UI/UX Features

### Upload Page
- Clean, modern design
- Large, obvious upload button
- Clear form labels
- Progress indicators
- Error messages
- Success toast notifications

### Assets Gallery
- Responsive grid layout
- Card-based design
- Status badges with color coding
- Quick search bar
- "View Full Details" button on each card
- Summary showing total assets

### Asset Detail View
- Large vehicle image
- Quick info cards at top
- Organized sections for:
  - Description
  - Driver History
  - AI Analysis Report
- Export and Delete buttons
- Professional typography

---

## 🔐 Data Security

- ✅ All Salesforce queries use parameterized input
- ✅ API requires CORS authentication
- ✅ Base64 image encoding for safe storage
- ✅ Proper error handling without exposing internals

---

## 📈 Performance

- ✅ Batch loading of vehicle data
- ✅ Efficient search/filter on frontend
- ✅ Lazy loading of assets
- ✅ Image optimization for display
- ✅ Caching opportunities for Salesforce queries

---

## 🚀 Future Enhancements

1. **Bulk Upload**: Import multiple vehicles at once
2. **Maintenance Tracking**: Log and track vehicle maintenance
3. **Cost Analysis**: Track fuel, repairs, depreciation
4. **Driver Performance**: Link to Webfleet driving scores
5. **Compliance Reports**: Generate audit reports
6. **Mobile App**: React Native version
7. **Real-time Updates**: WebSocket for live data
8. **Vehicle Timeline**: Visual history of all events

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review console logs
3. Check IMPLEMENTATION_SUMMARY.md
4. Verify Salesforce connection
5. Ensure all environment variables are set

---

## 📄 License

Part of Fleet Health Monitor system.

---

**Last Updated**: January 28, 2026
**Version**: 1.0.0
