# 🚗 Fleet Health Monitor - Quick Start

## ⚡ 3-Step Upload Process

### Step 1: Go to Upload
**Option A**: From home page → Click "Upload Vehicle" card
**Option B**: From dashboard → Click green "Upload Vehicle" button
**Option C**: Navigate directly to: `http://localhost:5173/upload`

### Step 2: Upload Image & Enter Van Number
```
1. Click image upload area
2. Select vehicle photo
3. Enter van number (e.g., "379")
4. Click "Search"
```

### Step 3: Auto-Filled Details
System automatically fetches:
- ✅ Registration Number (e.g., YB24UTN)
- ✅ Tracking Number (e.g., WZ5043I00082)
- ✅ Vehicle Type (e.g., Long wheel base high roof)
- ✅ Driver History (complete history)
- ✅ AI Analysis (vehicle condition assessment)

---

## 🖼️ View Asset Portfolio

### Option A: From Home Page
1. Click "Asset Portfolio" card (purple)
2. Browse grid of all uploaded vehicles
3. Click "View Full Details" on any vehicle

### Option B: From Dashboard
1. Click purple "Asset Portfolio" button
2. Browse and search vehicles
3. Click for details

### Option C: Direct URL
`http://localhost:5173/assets`

---

## 🔍 Search Uploaded Vehicles

**Search by**:
- Van number (e.g., "379")
- Registration (e.g., "YB24")
- Tracking number (e.g., "WZ504")
- Vehicle name (partial text)

**Supports partial matches** - type "37" to find "379"

---

## 📊 Dashboard Quick Links

### Available from Fleet Dashboard:

| Button | Color | Action |
|--------|-------|--------|
| Upload Vehicle | 🟢 Green | Go to upload page |
| Asset Portfolio | 🟣 Purple | Go to portfolio page |
| Driving Performance | 🔵 Blue | View driver scores |

### Dashboard KPI Cards (Clickable):
- Click any card to see vehicle list
- Allocated Vehicles
- Vehicles in Garage
- MOT Due
- Due for Service
- Spare Vehicles
- And more...

---

## 📱 Key Pages

| Page | URL | Purpose |
|------|-----|---------|
| **Home** | `/` | Landing page with quick links |
| **Dashboard** | `/fleet-dashboard` | Fleet overview and KPIs |
| **Upload** | `/upload` | Add new vehicles |
| **Portfolio** | `/assets` | View all uploaded vehicles |
| **Asset Details** | `/assets/379` | View specific vehicle details |
| **Performance** | `/webfleet` | Driver scores and rankings |

---

## 🎯 Complete Workflow

```
1. LOGIN/HOME
   └─→ See home page with quick cards

2. UPLOAD VEHICLE
   ├─→ Click "Upload Vehicle" button
   ├─→ Upload image (optional)
   ├─→ Enter van number
   ├─→ Auto-populated fields load
   └─→ Click "Save as Asset"

3. VIEW PORTFOLIO
   ├─→ Click "Asset Portfolio"
   ├─→ See grid of vehicles
   ├─→ Search/filter as needed
   └─→ Click "View Full Details" for specific vehicle

4. VEHICLE DETAILS
   ├─→ See all specifications
   ├─→ View driver history
   ├─→ Read AI analysis
   ├─→ Export if needed
   └─→ Or return to portfolio

5. CHECK PERFORMANCE
   ├─→ Click "Driving Performance"
   └─→ See engineer scores and rankings
```

---

## 💾 What Gets Saved

When you upload a vehicle:

✅ **Vehicle Info**
- Van number
- Registration number
- Tracking number
- Vehicle type
- Description

✅ **Media**
- Vehicle image (base64)

✅ **History**
- Complete driver history
- Usage records
- Service dates

✅ **AI Analysis**
- Condition assessment
- Safety evaluation
- Maintenance recommendations
- Damage assessment

✅ **Metadata**
- Upload date/time
- Status (Uploaded)
- Searchable fields

---

## 🚀 Features Enabled

### ✅ Working Now
- Fleet dashboard with KPIs
- Vehicle upload with image
- Auto-populate from Salesforce
- Asset portfolio gallery
- Vehicle search and filtering
- Asset detail view
- Driver performance scores
- AI vehicle analysis
- Export capabilities

### 🔄 In Development
- Bulk vehicle upload
- Advanced analytics/reports
- Mobile app version
- Real-time updates

---

## 🔐 Environment Setup

**Already Configured** (.env file):
```
SF_USERNAME=tech@aspect.co.uk
SF_PASSWORD=[configured]
WEBFLEET_ACCOUNT=maintenance-823
WEBFLEET_API_KEY=[configured]
```

**Optional** (AI Analysis):
- ANTHROPIC_API_KEY (for Claude vision API)

---

## 📞 Common Actions

### ✅ Action: Add a vehicle
1. Dashboard → Green button "Upload Vehicle"
2. Upload image
3. Enter van #
4. Auto-fill happens
5. Click Save

### ✅ Action: Find a vehicle
1. Dashboard → Purple button "Asset Portfolio"
2. Search by van/reg/tracking
3. Click "View Full Details"

### ✅ Action: Check driver performance
1. Dashboard → Blue button "Driving Performance"
2. See all engineer scores

### ✅ Action: Export vehicle details
1. Go to asset detail page
2. Click "Export" button
3. Download PDF/document

### ✅ Action: Delete a vehicle
1. Go to asset detail page
2. Click "Delete" button
3. Confirm deletion

---

## 🎨 UI Layout

### Home Page
- Hero section with app title
- 6 quick action cards
- Features highlight section

### Dashboard
- Top navigation with 3 buttons
- KPI cards grid (6 columns)
- Charts and analytics
- Clickable vehicle sheets

### Upload Page
- Left: Image upload
- Right: Van number search
- Center: Auto-populated fields
- Bottom: Driver history & AI analysis

### Portfolio Page
- Search bar at top
- Grid view of vehicles
- Status badges
- Quick info cards
- "View Full Details" button

### Asset Detail Page
- Header with vehicle name
- 4 quick info cards
- Large vehicle image
- Sections: Description, History, AI Analysis
- Export/Delete buttons

---

## 📊 Data Sources

| Data | Source |
|------|--------|
| Vehicle specs | Salesforce Vehicle__c |
| Driver history | Salesforce WorkOrder |
| Reg number | Salesforce Reg_No__c |
| Tracking | Salesforce Tracking_Number__c |
| Driver scores | Webfleet API |
| Images | User upload |
| AI Analysis | Claude Vision API |

---

## ✨ Next Steps

1. **Start**: Go to home page or dashboard
2. **Upload**: Click upload button
3. **Browse**: Click portfolio button
4. **View**: Click vehicle to see full details
5. **Manage**: Search, export, or delete as needed

---

**🎉 Everything is ready to use!**

Start by uploading your first vehicle or exploring the fleet dashboard.

---

**Version**: 1.0.0 | **Date**: January 28, 2026
