# Quick Test - Organization Authentication

## Start Servers

```bash
# Option 1: Double-click START_ALL.bat (easiest)

# Option 2: Manual
# Terminal 1:
cd backend
python app.py

# Terminal 2:
npm run dev
```

## Test Scenarios

### ✅ SHOULD WORK (Use these to test)

**Test with Aspect Company Account:**
1. Open http://localhost:5173
2. Click "Sign in with Microsoft"
3. Enter your @aspect.co.uk email
4. Should redirect to dashboard with your name in top-right

**Test with Demo Login:**
1. Open http://localhost:5173
2. Enter any email in the demo field
3. Click "Sign in"
4. Should immediately go to dashboard

### ❌ SHOULD FAIL (For verification)

**Test with Personal Gmail:**
1. Click "Sign in with Microsoft"
2. Try to sign in with personal Gmail account
3. **Expected Error**: "Only Aspect company accounts (@aspect.co.uk) are allowed"

**Test with Different Company Account:**
1. Click "Sign in with Microsoft"
2. Try to sign in with someone else's company account
3. **Expected Error**: "You must be logged into your Aspect company Microsoft account"

## Check Backend Logs

While testing, watch the backend terminal for messages like:

```
✅ Authorization code received
✅ User authenticated: [Name] ([email])
✅ Token verified for organization tenant
✅ User AUTHORIZED: [Name] ([email])
✅ Session created: [session_id]
✅ Redirect URL: http://localhost:5173/?user=...&email=...&session=...
```

OR

```
❌ REJECTED: User email domain not authorized: [email]
⚠️  Only @aspect.co.uk accounts are allowed
```

## Browser Console Logs

Press **F12** in browser and check Console tab for:

```
=== Login Component Mounted ===
Current URL: http://localhost:5173
Search params: {user: "...", email: "...", session: "..."}
✅ OAuth successful, user: [Name]
🔄 Navigating to dashboard...
```

## Summary

| Scenario | Result | User Sees |
|----------|--------|-----------|
| Aspect company email (@aspect.co.uk) | ✅ LOGIN SUCCESS | Dashboard with name |
| Personal email (Gmail, Yahoo, etc.) | ❌ REJECTED | Error message |
| Different company account | ❌ REJECTED | Error message |
| Demo login (any email) | ✅ LOGIN SUCCESS | Dashboard |

**Status: Organization-only authentication is now ACTIVE! 🔒**

