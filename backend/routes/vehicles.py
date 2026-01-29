from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from salesforce_service import SalesforceService

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])

@router.get("/lookup/{van_number}")
def lookup_vehicle_by_van(van_number: str):
    """
    Lookup vehicle information by van number
    Returns: registration number, tracking number, vehicle name, driver history, etc.
    """
    try:
        sf = SalesforceService()
        
        print(f"🔍 Looking up vehicle with van number: {van_number}")
        
        # Sanitize van_number - escape single quotes for SOQL
        sanitized_van = van_number.replace("'", "\\'")
        
        # Query vehicle by Van_Number__c
        vehicle_query = f"""
            SELECT 
                Id, 
                Name, 
                Van_Number__c, 
                Reg_No__c,
                Tracking_Number__c,
                Vehicle_Type__c,
                Description__c,
                Status__c
            FROM Vehicle__c
            WHERE Van_Number__c = '{sanitized_van}'
            LIMIT 1
        """
        
        print(f"📝 Query: {vehicle_query}")
        result = sf.sf.query_all(vehicle_query)
        records = result.get('records', [])
        
        if not records:
            print(f"❌ No vehicle found with van number: {van_number}")
            raise HTTPException(status_code=404, detail=f"Vehicle with van number {van_number} not found")
        
        vehicle = records[0]
        vehicle_id = vehicle.get('Id')
        
        print(f"✅ Found vehicle: {vehicle.get('Name')}")
        
        # Get complete driver history
        driver_history = get_driver_history(sf, vehicle_id)
        
        # Get driver name if associated
        driver_name = get_assigned_driver(sf, vehicle_id)
        
        # Prepare AI analysis context
        vehicle_info = f"""
        Vehicle: {vehicle.get('Name')}
        Van Number: {van_number}
        Registration: {vehicle.get('Reg_No__c')}
        Type: {vehicle.get('Vehicle_Type__c')}
        Status: {vehicle.get('Status__c')}
        Description: {vehicle.get('Description__c', 'N/A')}
        """
        
        return {
            "van_number": vehicle.get('Van_Number__c', van_number),
            "registration_number": vehicle.get('Reg_No__c', 'N/A'),
            "tracking_number": vehicle.get('Tracking_Number__c', 'N/A'),
            "vehicle_name": vehicle.get('Name', 'N/A'),
            "vehicle_type": vehicle.get('Vehicle_Type__c', 'N/A'),
            "description": vehicle.get('Description__c', 'N/A'),
            "status": vehicle.get('Status__c', 'N/A'),
            "driver_history": driver_history,
            "driver_name": driver_name,
            "vehicle_id": vehicle_id,
            "vehicle_info": vehicle_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error looking up vehicle: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def get_driver_history(sf: SalesforceService, vehicle_id: str) -> str:
    """Get complete driver history for a vehicle from Previous_Drivers__c field"""
    try:
        # Query the vehicle's Previous_Drivers__c field which contains the driver history
        history_query = f"""
            SELECT 
                Id, 
                Name,
                Van_Number__c,
                Previous_Drivers__c
            FROM Vehicle__c
            WHERE Id = '{vehicle_id}'
            LIMIT 1
        """
        
        print(f"📝 Driver history query: {history_query}")
        result = sf.sf.query_all(history_query)
        records = result.get('records', [])
        
        if not records:
            print(f"⚠️ No vehicle found with ID: {vehicle_id}")
            return "No driver history available"
        
        vehicle = records[0]
        previous_drivers = vehicle.get('Previous_Drivers__c', '')
        
        if previous_drivers:
            print(f"✅ Found driver history: {previous_drivers[:100]}...")
            return previous_drivers
        else:
            print(f"⚠️ No previous drivers found for vehicle {vehicle.get('Name')}")
            return "No driver history available"
        
    except Exception as e:
        print(f"❌ Error fetching driver history: {e}")
        import traceback
        traceback.print_exc()
        return f"Unable to fetch driver history: {str(e)}"


def get_assigned_driver(sf: SalesforceService, vehicle_id: str) -> str:
    """Get the assigned driver for a vehicle"""
    try:
        # Try to find ServiceResource assigned to this vehicle
        driver_query = f"""
            SELECT 
                Id, 
                Name,
                RelatedRecord.Name
            FROM ServiceResource
            WHERE Vehicle__c = '{vehicle_id}'
            LIMIT 1
        """
        
        result = sf.sf.query_all(driver_query)
        records = result.get('records', [])
        
        if records:
            return records[0].get('Name', 'N/A')
        
        return "No driver assigned"
        
    except Exception as e:
        print(f"⚠️ Error fetching assigned driver: {e}")
        return "Unable to fetch driver"


@router.get("/search")
def search_vehicles(q: str = ""):
    """Search for vehicles by van number, name, or registration"""
    try:
        sf = SalesforceService()
        
        print(f"🔍 Searching for vehicles matching: {q}")
        
        # Query all vehicles first
        vehicle_query = """
            SELECT 
                Id, 
                Name, 
                Van_Number__c, 
                Reg_No__c,
                Tracking_Number__c,
                Vehicle_Type__c,
                Status__c
            FROM Vehicle__c
            ORDER BY Van_Number__c ASC
            LIMIT 100
        """
        
        result = sf.sf.query_all(vehicle_query)
        records = result.get('records', [])
        
        # Filter results
        search_term = q.lower() if q else ""
        matching = []
        
        for record in records:
            van = record.get('Van_Number__c', '').lower()
            name = record.get('Name', '').lower()
            reg = record.get('Reg_No__c', '').lower()
            
            # Match if any field contains search term
            if not search_term or search_term in van or search_term in name or search_term in reg:
                matching.append({
                    "van_number": record.get('Van_Number__c'),
                    "name": record.get('Name'),
                    "registration_number": record.get('Reg_No__c'),
                    "vehicle_type": record.get('Vehicle_Type__c'),
                    "status": record.get('Status__c'),
                    "tracking_number": record.get('Tracking_Number__c')
                })
        
        print(f"✅ Found {len(matching)} matching vehicles")
        
        return {
            "search_term": q,
            "total_found": len(matching),
            "vehicles": matching[:20]  # Return first 20 results
        }
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
def list_all_vehicles():
    """List all vehicles stored as assets"""
    try:
        sf = SalesforceService()
        
        # Query all vehicles with their details
        vehicle_query = """
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
            ORDER BY Name ASC
        """
        
        result = sf.sf.query_all(vehicle_query)
        records = result.get('records', [])
        
        print(f"✅ Retrieved {len(records)} vehicles")
        
        vehicles = []
        for record in records:
            vehicles.append({
                "id": record.get('Id'),
                "name": record.get('Name'),
                "van_number": record.get('Van_Number__c'),
                "registration_number": record.get('Reg_No__c'),
                "tracking_number": record.get('Tracking_Number__c'),
                "vehicle_type": record.get('Vehicle_Type__c'),
                "description": record.get('Description'),
                "status": record.get('Status__c'),
                "created_date": record.get('CreatedDate')
            })
        
        return {
            "total": len(vehicles),
            "vehicles": vehicles
        }
        
    except Exception as e:
        print(f"❌ Error listing vehicles: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
