
import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()


class SalesforceService:
    """
    Pure Salesforce data access layer - NO intelligence, just execution
    """

    def __init__(self):
        """Initialize Salesforce connection"""
        username = os.getenv("SF_USERNAME")
        password = os.getenv("SF_PASSWORD")
        security_token = os.getenv("SF_SECURITY_TOKEN")
        domain = os.getenv("SF_DOMAIN", "login")

        if not all([username, password, security_token]):
            raise ValueError("❌ Missing Salesforce credentials")

        try:
            self.sf = Salesforce(
                username=username,
                password=password,
                security_token=security_token,
                domain=domain,
            )
            print("✅ Connected to Salesforce")
        except Exception as e:
            raise ConnectionError(f"❌ Failed to connect: {e}")

    def execute_soql(self, query: str) -> list:
        """Execute SOQL query and return ALL results with proper pagination"""
        try:
            print(f"🔍 Executing: {query[:150]}...")
            
            # Use query_all for automatic pagination
            result = self.sf.query_all(query)
            records = result.get("records", [])
            
            # Clean metadata from all records
            cleaned = []
            for r in records:
                clean_record = {}
                for k, v in r.items():
                    if not k.startswith('attributes'):
                        # Handle nested objects (like Vehicle__r.Name)
                        if isinstance(v, dict) and 'attributes' in v:
                            # Extract nested fields
                            nested_clean = {nk: nv for nk, nv in v.items() if not nk.startswith('attributes')}
                            clean_record[k] = nested_clean
                        else:
                            clean_record[k] = v
                cleaned.append(clean_record)
            
            print(f"✅ Returned {len(cleaned)} records (total in SF: {result.get('totalSize', len(cleaned))})")
            return cleaned
            
        except Exception as e:
            print(f"❌ SOQL Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    # ========================================
    # SIMPLE DATA RETRIEVAL METHODS
    # ========================================

    def get_all_vehicles(self) -> list:
        """Get ALL vehicles - NO LIMIT"""
        query = """
            SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                   Trade_Group__c, Vehicle_Type__c, Vehicle_Ownership__c,
                   Service_Territory__c
            FROM Vehicle__c
        """
        return self.execute_soql(query)

    def get_vehicle_by_identifier(self, identifier: str) -> dict:
        """Get vehicle by Name, Reg_No, or Van_Number"""
        query = f"""
            SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                   Trade_Group__c, Vehicle_Type__c, Vehicle_Ownership__c,
                   Lease_Start_Date__c, Owned_Start_Date__c,
                   Service_Territory__c, Make_Model__c, Description__c,
                   Previous_Drivers__c
            FROM Vehicle__c
            WHERE Name = '{identifier}' 
               OR Reg_No__c = '{identifier}' 
               OR Van_Number__c = '{identifier}'
            LIMIT 1
        """
        results = self.execute_soql(query)
        if results:
            print(f"✅ Found vehicle: {results[0].get('Name')} - {results[0].get('Reg_No__c')}")
            return results[0]
        else:
            print(f"❌ Vehicle not found: {identifier}")
            return None

    def get_vehicles_by_status(self, status: str) -> list:
        """Get vehicles by status - NO LIMIT"""
        query = f"""
            SELECT Id, Name, Reg_No__c, Van_Number__c, Status__c,
                   Trade_Group__c, Vehicle_Type__c
            FROM Vehicle__c
            WHERE Status__c = '{status}'
        """
        return self.execute_soql(query)

    def get_vehicle_allocations(self, vehicle_identifier: str = None) -> list:
        """Get current allocations - NO LIMIT"""
        if vehicle_identifier:
            where = f"(Vehicle__r.Name = '{vehicle_identifier}' OR Vehicle__r.Reg_No__c = '{vehicle_identifier}' OR Vehicle__r.Van_Number__c = '{vehicle_identifier}')"
        else:
            where = "End_date__c = null"

        query = f"""
            SELECT 
                Id, 
                Vehicle__r.Name, 
                Vehicle__r.Reg_No__c,
                Vehicle__r.Van_Number__c,
                Service_Resource__r.Name, 
                Service_Resource__r.Email,
                Internal_Staff__r.Name, 
                Internal_Staff__r.Email,
                Start_date__c, 
                End_date__c,
                Reserved_For__c
            FROM Vehicle_Allocation__c
            WHERE {where}
            ORDER BY Start_date__c DESC
        """
        results = self.execute_soql(query)
        print(f"📊 Allocations query returned {len(results)} records")
        return results

    def get_vehicle_costs(self, vehicle_identifier: str = None, limit: int = 100) -> list:
        """Get cost records"""
        if vehicle_identifier:
            where = f"Vehicle__r.Name = '{vehicle_identifier}' OR Vehicle__r.Reg_No__c = '{vehicle_identifier}' OR Vehicle__r.Van_Number__c = '{vehicle_identifier}'"
        else:
            where = "1=1"

        query = f"""
            SELECT 
                Vehicle__r.Name, 
                Vehicle__r.Reg_No__c,
                Type__c, 
                Payment_value__c, 
                Date__c, 
                Description__c
            FROM Vehicle_Cost__c
            WHERE {where}
            ORDER BY Date__c DESC
            LIMIT {limit}
        """
        return self.execute_soql(query)

    def get_vehicle_maintenance(self, vehicle_identifier: str = None) -> list:
        """Get maintenance info - NO LIMIT"""
        if vehicle_identifier:
            where = f"Name = '{vehicle_identifier}' OR Reg_No__c = '{vehicle_identifier}' OR Van_Number__c = '{vehicle_identifier}'"
        else:
            where = "Next_Service_Date__c != null OR Next_MOT_Date__c != null"

        query = f"""
            SELECT 
                Id, 
                Name, 
                Reg_No__c,
                Van_Number__c,
                Last_Service_Date__c, 
                Next_Service_Date__c,
                Last_MOT_Date__c, 
                Next_MOT_Date__c,
                Jetter__c, 
                Last_Jetter_Service__c, 
                Next_Jetter_Service__c
            FROM Vehicle__c
            WHERE {where}
            ORDER BY Next_Service_Date__c ASC NULLS LAST
        """
        return self.execute_soql(query)

    def get_vehicles_by_location(self, service_territory: str) -> list:
        """Get vehicles at location"""
        query = f"""
            SELECT 
                Id, 
                Name, 
                Reg_No__c, 
                Van_Number__c,
                Status__c,
                Trade_Group__c, 
                Service_Territory__c
            FROM Vehicle__c
            WHERE Service_Territory__c = '{service_territory}'
            ORDER BY Status__c
        """
        return self.execute_soql(query)

    def search_vehicle(self, search_term: str) -> list:
        """Search for vehicles by any field - useful for debugging"""
        query = f"""
            SELECT 
                Id, 
                Name, 
                Reg_No__c, 
                Van_Number__c, 
                Status__c,
                Trade_Group__c
            FROM Vehicle__c
            WHERE Name LIKE '%{search_term}%'
               OR Reg_No__c LIKE '%{search_term}%'
               OR Van_Number__c LIKE '%{search_term}%'
            LIMIT 10
        """
        return self.execute_soql(query)


# =========================
# 🧪 LOCAL TEST
# =========================
if __name__ == "__main__":
    print("🧪 Testing Salesforce Service\n")
    
    try:
        sf = SalesforceService()
        
        # Test 1: Count all vehicles
        print("=" * 60)
        print("Test 1: Get ALL vehicles")
        all_vehicles = sf.get_all_vehicles()
        print(f"✅ Total: {len(all_vehicles)} vehicles\n")
        
        # Test 2: Get allocated
        print("=" * 60)
        print("Test 2: Get allocated vehicles")
        allocated = sf.get_vehicles_by_status('Allocated')
        print(f"✅ Allocated: {len(allocated)} vehicles\n")
        
        # Test 3: Get all allocations
        print("=" * 60)
        print("Test 3: Get all current allocations")
        allocations = sf.get_vehicle_allocations()
        print(f"✅ Current allocations: {len(allocations)}")
        if allocations:
            print(f"   Sample: {allocations[0]}\n")
        
        # Test 4: Search for VEH-439
        print("=" * 60)
        print("Test 4: Search for VEH-439")
        vehicle = sf.get_vehicle_by_identifier('VEH-439')
        if vehicle:
            print(f"✅ Found: {vehicle}")
        else:
            print("❌ Not found - trying search...")
            results = sf.search_vehicle('439')
            print(f"   Search results: {results}\n")
        
        # Test 5: Get maintenance schedule
        print("=" * 60)
        print("Test 5: Get maintenance schedule")
        maintenance = sf.get_vehicle_maintenance()
        print(f"✅ Vehicles needing maintenance: {len(maintenance)}\n")
        
        print("=" * 60)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()