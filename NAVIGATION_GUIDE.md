# 🚗 Fleet Health Monitor - Quick Navigation Guide

## 🏠 Home Page (Landing Page)

**URL**: `http://localhost:5173/`

**Features**:
- Beautiful hero section with app title and description
- 6 quick action cards for easy navigation
- Feature highlights section
- One-click access to all main features

### Quick Action Cards Available:

1. **Fleet Dashboard** 🚗
   - View overall fleet status
   - Check vehicle counts and statuses
   - See maintenance schedules
   - Monitor KPIs

2. **Upload Vehicle** 📸
   - Add new vehicles with images
   - Auto-populate from Salesforce
   - AI analysis of vehicle condition
   - Save as asset

3. **Asset Portfolio** 🖼️
   - Browse all uploaded vehicles
   - Search and filter assets
   - View complete vehicle details
   - Portfolio management

4. **Driving Performance** ⚡
   - View engineer driving scores
   - OptiDrive metrics
   - Driver rankings
   - Performance analytics

5. **Analytics** (Coming Soon)
   - Fleet analytics
   - Reports generation

6. **Health Check** (Coming Soon)
   - Vehicle diagnostics
   - Maintenance recommendations

---

## 📊 Fleet Dashboard

**URL**: `http://localhost:5173/fleet-dashboard`

### Top Navigation Buttons:

#### 1️⃣ **Upload Vehicle** (Green Button)
- Click to go to vehicle upload page
- Upload image + enter van number
- Auto-fetch all details
- Save as asset

#### 2️⃣ **Asset Portfolio** (Purple Button)
- Browse all uploaded vehicle assets
- View vehicle gallery/portfolio
- Search and filter uploaded vehicles
- Access detailed asset information

#### 3️⃣ **View Driving Performance** (Blue Button)
- See engineer driving scores
- OptiDrive performance metrics
- Driver rankings

### Dashboard Sections:

**KPI Cards** (Click any card to view details):
- Current Vehicles
- Allocated Vehicles
- Vehicles in Garage
- Written Off Vehicles
- Due for Service
- Spare Vehicles
- MOT Due in 30 Days
- Road Tax Due

**Charts**:
- Trade Group Analysis
- Vehicle Type Distribution
- Spare Vehicles by Trade Group
- Leavers Vehicles Analysis
- Vehicle Data Sheet (clickable)

---

## 📸 Upload Vehicle Page

**URL**: `http://localhost:5173/upload`

### Workflow:

1. **Upload Image**
   - Click upload area or drag image
   - See preview on left side

2. **Enter Van Number**
   - Type van number (e.g., "379")
   - Click "Search" button

3. **Auto-Population**
   - System fetches from Salesforce:
     - ✅ Registration Number
     - ✅ Tracking Number
     - ✅ Vehicle Type
     - ✅ Vehicle Name
     - ✅ Driver History

4. **Review Information**
   - Check all populated fields
   - View driver history section
   - See AI analysis (if image provided)

5. **Save Asset**
   - Click "Save as Asset"
   - Vehicle is stored in system
   - Can now be viewed in Asset Portfolio

---

## 🖼️ Asset Portfolio Page

**URL**: `http://localhost:5173/assets`

### Features:

**Search Bar**:
- Search by van number
- Search by registration number
- Search by tracking number
- Search by vehicle name

**Asset Cards** (Grid View):
- Vehicle image preview
- Van number
- Registration number
- Tracking number
- Vehicle type
- Upload date
- Status badge

**Actions**:
- Click card to expand details
- Click "View Full Details" to go to asset detail page
- Summary showing total assets

---

## 📋 Asset Detail Page

**URL**: `http://localhost:5173/assets/379` (van number as ID)

### Displays:

**Quick Info Cards**:
- Van #: Large prominent display
- Registration Number
- Tracking Number
- Vehicle Type

**Vehicle Image Section**:
- Full size vehicle image
- Placeholder if no image

**Description Section**:
- Vehicle specifications
- Features and details

**Driver History Section**:
- Complete driver assignment history
- Usage history
- Service dates
- Maintenance records

**AI Analysis Report**:
- Vehicle condition assessment
- Visible damage analysis
- Cleanliness evaluation
- Safety observations
- Maintenance recommendations
- Driver behavior impact

**Actions**:
- Export: Download vehicle details
- Delete: Remove vehicle from system

---

## ⚡ Driving Performance Page

**URL**: `http://localhost:5173/webfleet`

### Features:

- Engineer/driver list
- Driving scores (0-10 scale)
- OptiDrive metrics
- Performance rankings
- Trade group breakdown
- Score classifications:
  - 🟢 Excellent (9-10)
  - 🟢 Good (8-8.9)
  - 🟡 Fair (7-7.9)
  - 🟠 Needs Improvement (6-6.9)
  - 🔴 Poor (0-5.9)

---

## 🔄 Navigation Flow

```
Home Page (Landing)
    ↓
    ├─→ Fleet Dashboard
    │       ├─→ Upload Vehicle → Upload Form → Asset Portfolio
    │       ├─→ Asset Portfolio → Asset Gallery → Asset Detail
    │       └─→ Driving Performance → Performance Scores
    │
    ├─→ Upload Vehicle → Upload Form → Asset Portfolio
    │
    ├─→ Asset Portfolio → Asset Gallery → Asset Detail
    │
    └─→ Driving Performance → Performance Scores
```

---

## 📱 Mobile Responsive

All pages are fully responsive:
- 📱 Mobile (1 column)
- 📱 Tablet (2 columns)
- 🖥️ Desktop (3+ columns)

---

## 🎨 Color Scheme

- 🔵 **Blue**: Fleet Dashboard, Performance
- 🟢 **Green**: Upload/Add functions
- 🟣 **Purple**: Portfolio/Gallery
- 🟠 **Orange**: Performance/Scores
- 🔴 **Red**: Delete/Danger actions
- ⚪ **Gray**: Disabled/Inactive

---

## ✅ Common Tasks

### Task 1: Add a New Vehicle
1. From home or dashboard, click "Upload Vehicle"
2. Upload vehicle image
3. Enter van number
4. System auto-fills all details
5. Click "Save as Asset"
6. View in Asset Portfolio

### Task 2: Find a Vehicle
1. Go to Asset Portfolio
2. Use search bar (van number, reg, tracking, or name)
3. Click "View Full Details" for complete info

### Task 3: Check Driver Performance
1. From dashboard or home, click "View Driving Performance"
2. See all engineer scores
3. Sorted by performance

### Task 4: View Vehicle Details
1. Go to Asset Portfolio
2. Click on vehicle card
3. Click "View Full Details"
4. See full specifications, history, and AI analysis

---

## 🔗 Direct URLs

| Page | URL |
|------|-----|
| Home | `/` |
| Fleet Dashboard | `/fleet-dashboard` |
| Upload Vehicle | `/upload` |
| Asset Portfolio | `/assets` |
| Asset Detail | `/assets/{van_number}` |
| Driving Performance | `/webfleet` |

---

## 💡 Tips

- **Quick Upload**: From dashboard, green "Upload Vehicle" button is fastest
- **Portfolio View**: Purple "Asset Portfolio" button shows all uploaded vehicles
- **Search**: Use partial van numbers (e.g., "37" finds "379")
- **Mobile**: All pages work great on phones and tablets
- **Export**: From asset detail page, click "Export" to download info
- **Delete**: Swipe or click delete button to remove assets

---

## 🆘 Need Help?

- **Upload not working?**: Check van number exists in Salesforce
- **Image not saving?**: Ensure file size < 5MB
- **Search not finding?**: Try different search term (partial match works)
- **AI analysis missing?**: Requires image upload and API configured
- **Auto-population empty?**: Check Salesforce connection

---

**Last Updated**: January 28, 2026
**Version**: 1.0.0
