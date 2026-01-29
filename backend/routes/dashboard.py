from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from salesforce_service import SalesforceService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def get_mot_due_count(sf):
    """Helper function to get MOT due count"""
    print("🔄 [get_mot_due_count] Starting MOT query...")
    try:
        query = """
            SELECT Id, Name
            FROM Vehicle__c
            WHERE Next_MOT_Date__c != NULL AND Next_MOT_Date__c <= NEXT_N_DAYS:30
        """
        print(f"🔍 [get_mot_due_count] Executing: {query.strip()}")
        vehicles = sf.execute_soql(query)
        count = len(vehicles) if vehicles else 0
        print(f"✅ [get_mot_due_count] Found {count} vehicles with Next_MOT_Date__c <= NEXT_N_DAYS:30")
        if count > 0 and vehicles:
            print(f"   Sample: {vehicles[0]}")
        return count
    except Exception as e:
        print(f"⚠️  [get_mot_due_count] Query failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def get_tax_due_count(sf):
    """Helper function to get Tax due count"""
    print("🔄 [get_tax_due_count] Starting Tax query...")
    try:
        query = """
            SELECT Id, Name
            FROM Vehicle__c
            WHERE Next_Tax_Date__c != NULL AND Next_Tax_Date__c <= NEXT_N_DAYS:30
        """
        print(f"🔍 [get_tax_due_count] Executing: {query.strip()}")
        vehicles = sf.execute_soql(query)
        count = len(vehicles) if vehicles else 0
        print(f"✅ [get_tax_due_count] Found {count} vehicles with Next_Tax_Date__c <= NEXT_N_DAYS:30")
        if count > 0 and vehicles:
            print(f"   Sample: {vehicles[0]}")
        return count
    except Exception as e:
        print(f"⚠️  [get_tax_due_count] Next_Tax_Date__c field failed: {e}")
        # Next_Tax_Date__c doesn't exist - return 0
        return 0


@router.get("/debug-statuses")
def debug_statuses():
    """
    DEBUG: Show all actual status values in Salesforce database
    """
    try:
        sf = SalesforceService()
        
        # Get all vehicles with their status values
        query = "SELECT Status__c FROM Vehicle__c"
        vehicles = sf.execute_soql(query)
        
        # Find unique status values
        unique_statuses = set()
        status_counts = {}
        
        for vehicle in vehicles:
            status = vehicle.get("Status__c")
            if status:
                unique_statuses.add(status)
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_vehicles": len(vehicles),
            "unique_statuses": sorted(list(unique_statuses)),
            "status_counts": status_counts,
        }
    except Exception as e:
        print(f"❌ Debug error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-mot-data")
def debug_mot_data():
    """
    DEBUG: Show sample vehicles with MOT data to understand the query issue
    """
    try:
        sf = SalesforceService()
        
        # Get a sample of vehicles with various fields to understand the data
        query = """
            SELECT Id, Name, Next_MOT_Date__c, YEAR(Next_MOT_Date__c) mot_year
            FROM Vehicle__c
            WHERE Next_MOT_Date__c != NULL
            ORDER BY Next_MOT_Date__c ASC
            LIMIT 10
        """
        try:
            vehicles = sf.execute_soql(query)
            return {
                "message": "Sample MOT vehicles (next 10 due)",
                "count": len(vehicles),
                "vehicles": vehicles
            }
        except Exception as e:
            print(f"Query with YEAR function failed: {e}")
            # Try simpler query
            query_simple = """
                SELECT Id, Name, Next_MOT_Date__c
                FROM Vehicle__c
                WHERE Next_MOT_Date__c != NULL
                ORDER BY Next_MOT_Date__c ASC
                LIMIT 10
            """
            vehicles = sf.execute_soql(query_simple)
            return {
                "message": "Sample MOT vehicles (next 10 due)",
                "count": len(vehicles),
                "vehicles": vehicles,
                "note": "This shows which vehicles have Next_MOT_Date__c set. Check if these dates are in the future."
            }
    except Exception as e:
        print(f"❌ Debug MOT error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "message": "Failed to fetch MOT sample data"
        }


@router.get("/debug-fields")
def debug_fields():
    """
    DEBUG: Show all available fields on Vehicle__c object by fetching a sample record
    """
    try:
        sf = SalesforceService()
        
        # Try to fetch a sample vehicle with all common date fields we know about
        query = """
            SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                   Trade_Group__c, Vehicle_Type__c, Make_Model__c,
                   Last_Service_Date__c, Next_Service_Date__c,
                   Next_MOT_Date__c, MOT_Due_Date__c,
                   Next_Tax_Date__c, Tax_Due_Date__c,
                   Last_MOT_Date__c, Last_Tax_Date__c
            FROM Vehicle__c
            LIMIT 1
        """
        try:
            vehicles = sf.execute_soql(query)
            if vehicles:
                sample = vehicles[0]
                # Show which date fields have values
                date_fields = {}
                for k, v in sample.items():
                    if 'date' in k.lower() or 'Date' in k:
                        date_fields[k] = v
                
                return {
                    "message": "Sample vehicle with known date fields",
                    "fields_with_values": list(date_fields.keys()),
                    "sample_record": sample,
                    "next_steps": "Check the 'fields_with_values' list to see which date fields exist in your Salesforce instance"
                }
        except Exception as e:
            print(f"Query with specific fields failed: {e}")
            # Try fetching just basic info
            query_basic = "SELECT Id, Name FROM Vehicle__c LIMIT 1"
            vehicles_basic = sf.execute_soql(query_basic)
            if vehicles_basic:
                return {
                    "message": "Could not query specific date fields. Trying alternative approach...",
                    "error": str(e),
                    "basic_record": vehicles_basic[0],
                    "hint": "Your Salesforce instance may not have the standard date fields. Please check the Vehicle__c object definition."
                }
            else:
                return {"error": "No vehicles found in Salesforce"}
    except Exception as e:
        print(f"❌ Debug fields error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "message": "Failed to fetch sample vehicle",
            "hint": "Ensure Salesforce credentials are correct in .env file"
        }


@router.get("/vehicle-summary")
def get_vehicle_summary():
    """
    Get vehicle summary counts by status from Salesforce.
    """
    try:
        sf = SalesforceService()
        
        # Fetch ALL vehicles
        all_vehicles_query = "SELECT Id, Status__c FROM Vehicle__c"
        vehicles = sf.execute_soql(all_vehicles_query)
        total = len(vehicles)
        
        print(f"📊 Total vehicles fetched: {total}")
        
        # Initialize status counts
        status_counts = {
            "allocated": 0,
            "garage": 0,
            "due_service": 0,
            "spare_ready": 0,
            "reserved": 0,
            "written_off": 0,
        }
        
        # ACTUAL Salesforce status values
        # Based on user's Salesforce data:
        # Allocated: 233, Reserved: 4, Sold: 15, Spare: 12, Spare Not Available: 4, Written Off: 21
        status_mapping = {
            # Allocated
            "Allocated": "allocated",
            "allocated": "allocated",
            
            # Garage/Service/Under Repair
            "Garage": "garage",
            "garage": "garage",
            "In Garage": "garage",
            "Under Repair": "garage",
            
            # Due Service
            "Due for Service": "due_service",
            "Due_Service": "due_service",
            "Service Due": "due_service",
            
            # Spare Ready (includes all spare variants)
            "Spare Ready": "spare_ready",
            "Spare_Ready": "spare_ready",
            "Spare": "spare_ready",
            "Spare Tankers": "spare_ready",
            "Spare in Garage": "spare_ready",
            "Spare Not Available": "spare_ready",  # Include in spare count
            
            # Reserved
            "Reserved": "reserved",
            "reserved": "reserved",
            
            # Written Off
            "Written Off": "written_off",
            "Written_Off": "written_off",
            
            # Note: "Sold" not mapped - vehicles that are sold are not counted in active fleet
            # Note: Unmapped statuses are silently ignored
        }
        
        # Aggregate locally
        status_values_found = {}
        unmapped_statuses = {}
        for vehicle in vehicles:
            sf_status = vehicle.get("Status__c")
            if sf_status:
                if sf_status not in status_values_found:
                    status_values_found[sf_status] = 0
                status_values_found[sf_status] += 1
                
                response_key = status_mapping.get(sf_status)
                if response_key:
                    status_counts[response_key] += 1
                else:
                    # Track unmapped statuses
                    if sf_status not in unmapped_statuses:
                        unmapped_statuses[sf_status] = 0
                    unmapped_statuses[sf_status] += 1
        
        print(f"✅ Status values found in Salesforce:")
        for status, count in sorted(status_values_found.items()):
            print(f"   '{status}': {count}")
        print(f"✅ Mapped status counts: {status_counts}")
        if unmapped_statuses:
            print(f"⚠️  Unmapped statuses (not included in counts): {unmapped_statuses}")
        
        # Get MOT and Tax due counts using helper functions
        print("📊 Getting MOT due count...")
        mot_due = get_mot_due_count(sf)
        
        print("📊 Getting Tax due count...")
        tax_due = get_tax_due_count(sf)
        
        print(f"📊 SUMMARY RESULT: MOT={mot_due}, Tax={tax_due}")
        
        return {
            "total": total,
            **status_counts,
            "mot_due": mot_due,
            "tax_due": tax_due,
        }
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vehicles-by-status/{status}")
def get_vehicles_by_status(status: str):
    """
    Get all vehicles with a specific status
    """
    try:
        sf = SalesforceService()
        
        # Map friendly status names to Salesforce values (allow multiple SF statuses)
        status_map = {
            "allocated": ["Allocated"],
            "garage": ["Garage"],
            "due_service": ["Due for Service", "Service Due", "Due_Service"],
            "spare_ready": ["Spare", "Spare Not Available"],  # ACTUAL Salesforce values only
            "reserved": ["Reserved"],
            "written_off": ["Written Off"],
            "sold": ["Sold"],
            "total": [],  # Empty = return ALL vehicles
            "current": [],  # Empty = return ALL vehicles
        }

        # 'current' or 'total' -> return all vehicles (no status filter)
        key = status.lower()
        sf_values = status_map.get(key)
        
        # Build query based on status
        if key == 'current' or key == 'total' or (sf_values is not None and len(sf_values) == 0):
            where_clause = ""
            sf_status = 'ALL'
        elif sf_values and len(sf_values) > 1:
            # Multiple values: use IN clause
            values_str = ",".join([f"'{v}'" for v in sf_values])
            where_clause = f"WHERE Status__c IN ({values_str})"
            sf_status = " | ".join(sf_values)
        elif sf_values and len(sf_values) == 1:
            # Single value: use = clause
            where_clause = f"WHERE Status__c = '{sf_values[0]}'"
            sf_status = sf_values[0]
        else:
            # Unmapped status: treat as literal
            where_clause = f"WHERE Status__c = '{status}'"
            sf_status = status

        query = f"""
            SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c, 
                   Trade_Group__c, Vehicle_Type__c, Make_Model__c,
                   Last_Service_Date__c, Next_Service_Date__c,
                   Last_MOT_Date__c, Next_MOT_Date__c
            FROM Vehicle__c
            {where_clause}
            ORDER BY Name
        """
        
        print(f"🔍 Query: {query[:100]}...")
        vehicles = sf.execute_soql(query)

        print(f"🔍 Found {len(vehicles)} vehicles with status '{sf_status}'")

        # If we have vehicles, aggregate cost data from Vehicle_Cost__c
        if vehicles:
            vehicle_ids = [v.get('Id') for v in vehicles if v.get('Id')]
            if vehicle_ids:
                ids_escaped = ", ".join([f"'{vid}'" for vid in vehicle_ids])

                # Total cost per vehicle
                cost_query = f"""
                    SELECT Vehicle__c, SUM(Payment_value__c) total
                    FROM Vehicle_Cost__c
                    WHERE Vehicle__c IN ({ids_escaped})
                    GROUP BY Vehicle__c
                """
                cost_results = sf.execute_soql(cost_query)
                cost_map = {r.get('Vehicle__c'): r.get('total', 0) for r in cost_results}

                # Maintenance-related cost per vehicle (Type__c contains Service or Maint)
                maint_query = f"""
                    SELECT Vehicle__c, SUM(Payment_value__c) maintenance_total
                    FROM Vehicle_Cost__c
                    WHERE Vehicle__c IN ({ids_escaped}) AND (Type__c LIKE '%Service%' OR Type__c LIKE '%Maint%')
                    GROUP BY Vehicle__c
                """
                maint_results = sf.execute_soql(maint_query)
                maint_map = {r.get('Vehicle__c'): r.get('maintenance_total', 0) for r in maint_results}

                # Attach cost values to vehicle records
                for v in vehicles:
                    vid = v.get('Id')
                    v['service_cost'] = cost_map.get(vid, 0)
                    v['maintenance_cost'] = maint_map.get(vid, 0)
        
        return {
            "status": sf_status,
            "count": len(vehicles),
            "vehicles": vehicles,
        }
        
    except Exception as e:
        print(f"❌ Error fetching vehicles by status: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vehicles-mot-due")
def get_vehicles_mot_due(days: int = 30):
    """
    Get vehicles with MOT due within the next `days` days (default 30).
    """
    try:
        sf = SalesforceService()
        # Use SOQL date literal NEXT_N_DAYS: to filter
        query = f"""
            SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                   Trade_Group__c, Vehicle_Type__c, Make_Model__c,
                   Last_MOT_Date__c, Next_MOT_Date__c
            FROM Vehicle__c
            WHERE Next_MOT_Date__c != NULL AND Next_MOT_Date__c <= NEXT_N_DAYS:{days}
            ORDER BY Next_MOT_Date__c ASC
        """
        vehicles = sf.execute_soql(query)
        print(f"✅ MOT due vehicles found: {len(vehicles)}")
        return {"count": len(vehicles), "vehicles": vehicles}
    except Exception as e:
        print(f"❌ Error fetching MOT due vehicles: {e}")
        import traceback
        traceback.print_exc()
        # Try alternative field name
        try:
            print("🔄 Trying alternative field name MOT_Due_Date__c...")
            query_alt = f"""
                SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                       Trade_Group__c, Vehicle_Type__c, Make_Model__c
                FROM Vehicle__c
                WHERE MOT_Due_Date__c != NULL AND MOT_Due_Date__c <= NEXT_N_DAYS:{days}
                ORDER BY MOT_Due_Date__c ASC
            """
            vehicles_alt = sf.execute_soql(query_alt)
            print(f"✅ MOT due vehicles (alt) found: {len(vehicles_alt)}")
            return {"count": len(vehicles_alt), "vehicles": vehicles_alt}
        except:
            print("⚠️  Alternative field name also failed, returning empty list")
            return {"count": 0, "vehicles": []}


@router.get("/vehicles-tax-due")
def get_vehicles_tax_due(days: int = 30):
    """
    Get vehicles with road tax due within the next `days` days (default 30).
    """
    try:
        sf = SalesforceService()
        query = f"""
            SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                   Trade_Group__c, Vehicle_Type__c, Make_Model__c,
                   Last_Tax_Date__c, Next_Tax_Date__c
            FROM Vehicle__c
            WHERE Next_Tax_Date__c != NULL AND Next_Tax_Date__c <= NEXT_N_DAYS:{days}
            ORDER BY Next_Tax_Date__c ASC
        """
        vehicles = sf.execute_soql(query)
        print(f"✅ Tax due vehicles found: {len(vehicles)}")
        return {"count": len(vehicles), "vehicles": vehicles}
    except Exception as e:
        print(f"❌ Error fetching road tax due vehicles: {e}")
        import traceback
        traceback.print_exc()
        # Try alternative field name
        try:
            print("🔄 Trying alternative field name Tax_Due_Date__c...")
            query_alt = f"""
                SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                       Trade_Group__c, Vehicle_Type__c, Make_Model__c
                FROM Vehicle__c
                WHERE Tax_Due_Date__c != NULL AND Tax_Due_Date__c <= NEXT_N_DAYS:{days}
                ORDER BY Tax_Due_Date__c ASC
            """
            vehicles_alt = sf.execute_soql(query_alt)
            print(f"✅ Tax due vehicles (alt) found: {len(vehicles_alt)}")
            return {"count": len(vehicles_alt), "vehicles": vehicles_alt}
        except:
            print("⚠️  Alternative field name also failed, returning empty list")
            return {"count": 0, "vehicles": []}
