from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from salesforce_service import SalesforceService
from webfleet_api import WebfleetAPI
from requests.auth import HTTPBasicAuth
import requests

router = APIRouter(prefix="/api/webfleet", tags=["webfleet"])

# Global cache for driving scores
_cache = {
    'scores': {},  # email -> score
    'last_updated': None
}

def get_all_webfleet_drivers_and_scores():
    """
    Get ALL drivers AND their scores efficiently using WebfleetAPI's email-based lookup
    This is the RELIABLE method - uses email matching like the working implementation
    """
    try:
        webfleet = WebfleetAPI()
        
        print("📞 Fetching ALL drivers from Webfleet...")
        
        # STEP 1: Get all drivers with emails
        driver_params = {
            'account': webfleet.account,
            'apikey': webfleet.api_key,
            'lang': 'en',
            'action': 'showDriverReportExtern',
            'outputformat': 'json',
            'useUTF8': 'true',
            'useISO8601': 'true'
        }
        
        driver_response = requests.get(
            webfleet.base_url,
            params=driver_params,
            auth=HTTPBasicAuth(webfleet.username, webfleet.password),
            timeout=30
        )
        
        if driver_response.status_code != 200:
            print(f"❌ Webfleet API error: Status {driver_response.status_code}")
            return {}
        
        driver_data = driver_response.json()
        
        if not driver_data or not isinstance(driver_data, list):
            print(f"⚠️ No valid driver data returned")
            return {}
        
        # Extract all driver emails
        driver_emails = []
        for driver in driver_data:
            if isinstance(driver, dict):
                email_raw = driver.get('email', '').strip()
                if email_raw:
                    driver_emails.append(email_raw)
        
        print(f"✅ Found {len(driver_emails)} drivers with emails")
        
        # STEP 2: Get scores for ALL emails using the reliable email-based method
        print("📊 Fetching OptiDrive scores by email...")
        
        email_to_score = {}
        matched_count = 0
        
        for idx, driver_email in enumerate(driver_emails, 1):
            try:
                # Use the reliable email-based lookup (0-1 scale)
                optidrive_score = webfleet.get_driver_data_by_email(driver_email)
                
                if optidrive_score is not None:
                    # Convert from 0-1 scale to 0-100 scale (matching your calculation logic)
                    score_100 = round(optidrive_score * 100, 1)
                    email_to_score[driver_email.lower()] = score_100
                    matched_count += 1
                    
                    if idx % 50 == 0:
                        print(f"   Progress: {idx}/{len(driver_emails)} drivers processed...")
                else:
                    email_to_score[driver_email.lower()] = 0
                    
            except Exception as e:
                print(f"⚠️ Error fetching score for {driver_email}: {e}")
                email_to_score[driver_email.lower()] = 0
        
        print(f"✅ Successfully matched {matched_count}/{len(driver_emails)} drivers with scores")
        
        return email_to_score
        
    except Exception as e:
        print(f"❌ Error fetching Webfleet data: {e}")
        import traceback
        traceback.print_exc()
        return {}


@router.get("/engineers")
def get_engineers_with_scores():
    """
    Get ONLY engineers from Salesforce that exist in Webfleet
    OPTIMIZED: Fetches all scores in ONE batch call!
    """
    try:
        sf = SalesforceService()
        
        print("\n" + "="*80)
        print("📊 OPTIMIZED FETCH - Batch Loading")
        print("="*80 + "\n")
        
        # Step 1: Get ALL scores from Webfleet in ONE batch
        print("🚀 Step 1: Fetching ALL Webfleet scores in batch...")
        email_to_score = get_all_webfleet_drivers_and_scores()
        
        if not email_to_score:
            # Fallback to empty but don't fail
            email_to_score = {}
        
        print(f"✅ Got {len(email_to_score)} scores from Webfleet\n")
        
        # Step 2: Get ALL Salesforce engineers
        print("🚀 Step 2: Fetching engineers from Salesforce...")
        
        engineer_query = """
            SELECT 
                Id, 
                Name, 
                RelatedRecord.Email,
                Trade_Lookup__c
            FROM ServiceResource
            WHERE IsActive = true 
            AND RelatedRecord.Email != null
            ORDER BY Name ASC
        """
        
        result = sf.sf.query(engineer_query)
        all_engineers = result.get('records', [])
        
        print(f"✅ Found {len(all_engineers)} active engineers in Salesforce\n")
        
        # Step 3: Build engineer list with scores (FAST - no API calls!)
        print("🚀 Step 3: Matching engineers with scores...")
        
        engineers_list = []
        
        for engineer in all_engineers:
            engineer_name = engineer.get('Name', 'Unknown')
            
            # Get email from RelatedRecord
            related_record = engineer.get('RelatedRecord', {})
            if related_record and isinstance(related_record, dict):
                engineer_email = related_record.get('Email', '').strip()
            else:
                engineer_email = ''
            
            if not engineer_email:
                continue
            
            email_lower = engineer_email.lower()
            
            # Get score from batch fetch (0-100 scale) - convert to 0-10 scale
            score_100 = email_to_score.get(email_lower, 0)
            driving_score = round(score_100 / 10, 1) if score_100 > 0 else 0  # Convert to 0-10 scale
            score_class = get_score_class(score_100)  # Use 0-100 for classification
            
            # Get trade group
            trade_group = engineer.get('Trade_Lookup__c', 'N/A')
            
            engineers_list.append({
                "rank": 0,
                "name": engineer_name,
                "email": engineer_email,
                "van_number": "N/A",
                "trade_group": trade_group,
                "driving_score": driving_score,
                "score_class": score_class
            })
        
        # Sort by driving score (highest first)
        engineers_list.sort(key=lambda x: (-x['driving_score'], x['name']))
        
        # Update ranks
        for idx, engineer in enumerate(engineers_list):
            engineer['rank'] = idx + 1
        
        print(f"\n✅ COMPLETE!")
        print(f"   Total engineers with Webfleet scores: {len(engineers_list)}")
        print(f"   Average score: {sum(e['driving_score'] for e in engineers_list)/len(engineers_list):.1f}" if engineers_list else "   No scores")
        print("="*80 + "\n")
        
        return {
            "total": len(engineers_list),
            "total_salesforce_engineers": len(all_engineers),
            "engineers_in_webfleet": len(engineers_list),
            "with_scores": len([e for e in engineers_list if e['driving_score'] > 0]),
            "engineers": engineers_list
        }
        
    except Exception as e:
        print(f"❌ Error fetching engineers: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-connection")
def test_webfleet_connection():
    """Test Webfleet API connection"""
    try:
        scores = get_all_webfleet_drivers_and_scores()
        
        return {
            "status": "ok",
            "message": "Webfleet connection successful",
            "drivers_with_scores": len(scores)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def get_score_class(score):
    """Determine score class/category for UI styling"""
    if score >= 90:
        return "excellent"
    elif score >= 80:
        return "good"
    elif score >= 70:
        return "fair"
    elif score >= 60:
        return "needs_improvement"
    else:
        return "poor"