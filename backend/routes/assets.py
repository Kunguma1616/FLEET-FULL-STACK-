from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from salesforce_service import SalesforceService

router = APIRouter(prefix="/api/assets", tags=["assets"])

class VehicleAsset(BaseModel):
    van_number: str
    registration_number: str
    tracking_number: str
    vehicle_name: str
    driver_history: str
    vehicle_type: str
    description: str
    ai_details: str = ""
    image_data: str = ""  # Base64 encoded image


@router.post("/create")
def create_asset(asset: VehicleAsset):
    """
    Create a new vehicle asset with all details
    Stores image, driver history, AI analysis, etc.
    """
    try:
        sf = SalesforceService()
        
        print(f"📝 Creating asset for vehicle: {asset.van_number}")
        print(f"📋 Asset data received: van={asset.van_number}, reg={asset.registration_number}, tracking={asset.tracking_number}")
        
        # First, check if vehicle already exists by van number
        existing_vehicle_query = f"""
            SELECT Id, Status__c FROM Vehicle__c 
            WHERE Van_Number__c = '{asset.van_number}'
            LIMIT 1
        """
        
        result = sf.sf.query_all(existing_vehicle_query)
        existing_records = result.get('records', [])
        
        # Prepare vehicle data - MINIMAL fields only
        vehicle_data = {
            "Van_Number__c": asset.van_number,
            "Reg_No__c": asset.registration_number,
            "Tracking_Number__c": asset.tracking_number
        }
        
        print(f"📋 Minimal vehicle data to save: {vehicle_data}")
        
        if existing_records:
            # Update existing vehicle - ONLY update the three essential fields
            vehicle_id = existing_records[0].get('Id')
            current_status = existing_records[0].get('Status__c', 'Unknown')
            print(f"✏️ Updating existing vehicle: {vehicle_id} (current status: {current_status})")
            sf.sf.Vehicle__c.update(vehicle_id, vehicle_data)
            vehicle_id_result = vehicle_id
        else:
            # Create new vehicle
            print(f"✨ Creating new vehicle")
            # Add required fields for creation
            vehicle_data["Name"] = asset.vehicle_name or f"Vehicle {asset.van_number}"
            vehicle_data["Status__c"] = "Spare"
            result = sf.sf.Vehicle__c.create(vehicle_data)
            vehicle_id_result = result['id']
        
        print(f"✅ Vehicle saved with ID: {vehicle_id_result}")
        
        return {
            "status": "success",
            "message": "Asset created successfully",
            "vehicle_id": vehicle_id_result,
            "van_number": asset.van_number
        }
        
    except Exception as e:
        print(f"❌ Error creating asset: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-van/{van_number}")
def get_asset_by_van(van_number: str):
    """Get asset details by van number"""
    try:
        sf = SalesforceService()
        
        print(f"🔍 Retrieving asset: {van_number}")
        
        # Query vehicle with all details
        query = f"""
            SELECT 
                Id, 
                Name, 
                Van_Number__c, 
                Reg_No__c,
                Tracking_Number__c,
                Vehicle_Type__c,
                Description__c,
                Status__c,
                CreatedDate
            FROM Vehicle__c
            WHERE Van_Number__c = '{van_number}'
            LIMIT 1
        """
        
        result = sf.sf.query_all(query)
        records = result.get('records', [])
        
        if not records:
            raise HTTPException(status_code=404, detail=f"Asset not found for van {van_number}")
        
        vehicle = records[0]
        
        return {
            "id": vehicle.get('Id'),
            "name": vehicle.get('Name'),
            "van_number": vehicle.get('Van_Number__c'),
            "registration_number": vehicle.get('Reg_No__c'),
            "tracking_number": vehicle.get('Tracking_Number__c'),
            "vehicle_type": vehicle.get('Vehicle_Type__c'),
            "description": vehicle.get('Description__c'),
            "status": vehicle.get('Status__c'),
            "created_date": vehicle.get('CreatedDate')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
def get_all_assets():
    """Get all uploaded vehicle assets"""
    try:
        sf = SalesforceService()
        
        print(f"📋 Retrieving all assets...")
        
        # Query all vehicles (no status filter - show all vehicles)
        query = """
            SELECT 
                Id, 
                Name, 
                Van_Number__c, 
                Reg_No__c,
                Tracking_Number__c,
                Vehicle_Type__c,
                Description__c,
                Status__c,
                CreatedDate
            FROM Vehicle__c
            ORDER BY CreatedDate DESC
        """
        
        result = sf.sf.query_all(query)
        records = result.get('records', [])
        
        print(f"✅ Retrieved {len(records)} assets")
        
        assets = []
        for record in records:
            assets.append({
                "id": record.get('Id'),
                "name": record.get('Name'),
                "van_number": record.get('Van_Number__c'),
                "registration_number": record.get('Reg_No__c'),
                "tracking_number": record.get('Tracking_Number__c'),
                "vehicle_type": record.get('Vehicle_Type__c'),
                "description": record.get('Description__c'),
                "status": record.get('Status__c'),
                "created_date": record.get('CreatedDate')
            })
        
        return {
            "total": len(assets),
            "assets": assets
        }
        
    except Exception as e:
        print(f"❌ Error retrieving assets: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
