from fastapi import APIRouter, HTTPException, Request, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta
import secrets
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Store sessions in memory (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}

# Microsoft OAuth Configuration
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "common")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class AuthSession(BaseModel):
    user: Dict[str, str]
    session: str


class UserInfo(BaseModel):
    name: str
    email: str
    session_id: str


def create_session(user_data: Dict[str, str]) -> str:
    """Create a new session"""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "user": user_data,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    print(f"✅ Session created: {session_id}")
    return session_id


def get_session_user(session_id: str) -> Optional[Dict[str, str]]:
    """Get user from session"""
    session = sessions.get(session_id)
    if session:
        if datetime.now() < session["expires_at"]:
            return session["user"]
        else:
            del sessions[session_id]
    return None


def clear_session(session_id: str) -> bool:
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]
        print(f"✅ Session cleared: {session_id}")
        return True
    return False


@router.get("/microsoft")
async def microsoft_signin():
    """Redirect to Microsoft OAuth"""
    redirect_uri = f"{BACKEND_URL}/api/auth/callback/microsoft"
    
    microsoft_auth_url = (
        f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
        f"?client_id={MICROSOFT_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&response_mode=query"
        f"&scope=openid%20profile%20email%20User.Read"
    )
    
    print(f"🔐 Redirecting to Microsoft: {microsoft_auth_url[:100]}...")
    return RedirectResponse(url=microsoft_auth_url)


@router.get("/callback/microsoft")
async def microsoft_callback(code: str = Query(None), error: str = Query(None)):
    """Handle Microsoft OAuth callback"""
    print("\n" + "="*60)
    print("Microsoft OAuth Callback")
    print("="*60)
    
    if error:
        print(f"❌ Error: {error}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?error={error}"
        )
    
    if not code:
        print("❌ No authorization code received")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?error=no_code"
        )
    
    print(f"✅ Authorization code received")
    
    try:
        # Exchange code for access token
        token_url = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
        redirect_uri = f"{BACKEND_URL}/api/auth/callback/microsoft"
        
        token_response = requests.post(
            token_url,
            data={
                'client_id': MICROSOFT_CLIENT_ID,
                'client_secret': MICROSOFT_CLIENT_SECRET,
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            }
        )
        
        token_data = token_response.json()
        
        if 'error' in token_data:
            print(f"❌ Token exchange error: {token_data}")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?error=token_exchange_failed"
            )
        
        access_token = token_data.get('access_token')
        if not access_token:
            print("❌ No access token received")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?error=no_token"
            )
        
        # Get user info from Microsoft Graph API
        user_response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        user_data = user_response.json()
        
        if 'error' in user_data:
            print(f"❌ User info error: {user_data}")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?error=user_info_failed"
            )
        
        user_email = user_data.get('mail') or user_data.get('userPrincipalName')
        user_name = user_data.get('displayName') or user_email
        
        print(f"✅ User authenticated: {user_name} ({user_email})")
        
        # ===== ORGANIZATION VALIDATION =====
        # Check if user's email is from the allowed organization domain
        ALLOWED_EMAIL_DOMAIN = "@aspect.co.uk"
        
        if not user_email or ALLOWED_EMAIL_DOMAIN not in user_email.lower():
            print(f"❌ REJECTED: User email domain not authorized: {user_email}")
            print(f"⚠️  Only {ALLOWED_EMAIL_DOMAIN} accounts are allowed")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?error=unauthorized_domain&email={user_email}"
            )
        
        # Verify the token came from the correct tenant
        token_claims = token_data.get('id_token')
        if token_claims:
            # Decode token to check tenant info (basic validation)
            import base64
            try:
                # JWT format: header.payload.signature
                parts = token_claims.split('.')
                if len(parts) >= 2:
                    # Add padding if needed
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.urlsafe_b64decode(payload)
                    import json
                    token_data_decoded = json.loads(decoded)
                    
                    token_tenant_id = token_data_decoded.get('tid')
                    if token_tenant_id and token_tenant_id != MICROSOFT_TENANT_ID:
                        print(f"❌ REJECTED: Token from wrong tenant: {token_tenant_id}")
                        print(f"❌ Expected tenant: {MICROSOFT_TENANT_ID}")
                        return RedirectResponse(
                            url=f"{FRONTEND_URL}/?error=wrong_tenant"
                        )
                    print(f"✅ Token verified for organization tenant")
            except Exception as e:
                print(f"⚠️  Could not verify token tenant: {e}")
        
        print(f"✅ User AUTHORIZED: {user_name} ({user_email})")
        
        # Create session
        user_info = {
            "name": user_name,
            "email": user_email
        }
        session_id = create_session(user_info)
        
        # Properly encode the redirect URL
        redirect_params = {
            "user": user_name,
            "email": user_email,
            "session": session_id
        }
        redirect_url = f"{FRONTEND_URL}/?{urlencode(redirect_params)}"
        print(f"✅ Redirect URL: {redirect_url}")
        print(f"✅ Redirecting to dashboard with session: {session_id}")
        print("="*60 + "\n")
        
        return RedirectResponse(url=redirect_url)
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?error=exception"
        )


@router.post("/session")
async def create_session_endpoint(user_data: Dict[str, str]) -> Dict[str, str]:
    """Create a new session"""
    session_id = create_session(user_data)
    return {
        "session_id": session_id,
        "expires_in": "24h"
    }


@router.get("/session/{session_id}")
async def get_session_endpoint(session_id: str) -> AuthSession:
    """Get session info"""
    user = get_session_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return AuthSession(
        user=user,
        session="active"
    )


@router.post("/logout/{session_id}")
async def logout(session_id: str) -> Dict[str, bool]:
    """Logout user"""
    clear_session(session_id)
    return {"success": True}


@router.get("/verify/{session_id}")
async def verify_session(session_id: str) -> Dict[str, Any]:
    """Verify if session is valid"""
    user = get_session_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return {
        "valid": True,
        "user": user,
        "expires_in": "24h"
    }
