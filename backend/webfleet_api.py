import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import os
import re

class WebfleetAPI:
    """Handle Webfleet API calls for driving scores"""
    
    def __init__(self):
        self.base_url = "https://csv.webfleet.com/extern"
        self.username = os.getenv('WEBFLEET_USERNAME')
        self.password = os.getenv('WEBFLEET_PASSWORD')
        self.account = os.getenv('WEBFLEET_ACCOUNT')
        self.api_key = os.getenv('WEBFLEET_API_KEY')
    
    def get_driver_data_by_email(self, driver_email):
        """
        Get driver data (including driving score) by email address
        Returns the optidrive_indicator (0-1 scale, where 1 is perfect)
        
        This is the PREFERRED method - more accurate than name matching
        """
        try:
            # Get date range (last 7 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Format dates as YYYYMMDD
            range_from = start_date.strftime('%Y%m%d')
            range_to = end_date.strftime('%Y%m%d')
            
            # STEP 1: Get all drivers to find by email
            driver_params = {
                'account': self.account,
                'apikey': self.api_key,
                'lang': 'en',
                'action': 'showDriverReportExtern',
                'outputformat': 'json',
                'useUTF8': 'true',
                'useISO8601': 'true'
            }
            
            # print(f"📞 Calling Webfleet API to find driver by email: {driver_email}")
            
            # Get all drivers
            driver_response = requests.get(
                self.base_url,
                params=driver_params,
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=10
            )
            
            if driver_response.status_code != 200:
                print(f"❌ Webfleet API error: Status {driver_response.status_code}")
                return None
            
            driver_data = driver_response.json()
            
            if not driver_data or not isinstance(driver_data, list):
                print(f"⚠️ No valid driver data returned")
                return None
            
            # STEP 2: Find driver by email
            matching_driver = None
            driver_name_in_webfleet = None
            
            for driver in driver_data:
                if not isinstance(driver, dict):
                    continue
                
                driver_email_from_api = driver.get('email', '').strip().lower()
                
                if driver_email_from_api == driver_email.strip().lower():
                    matching_driver = driver
                    driver_name_in_webfleet = driver.get('name1', '')
                    # print(f"✓ Found driver by email: {driver.get('name1')} ({driver_email})")
                    break
            
            if not matching_driver or not driver_name_in_webfleet:
                # print(f"⚠️ No driver found with email: {driver_email}")
                return None
            
            # STEP 3: Get OptiDrive score using the driver's name from Webfleet
            optidrive_params = {
                'account': self.account,
                'apikey': self.api_key,
                'lang': 'en',
                'action': 'showOptiDriveIndicator',
                'rangefrom_string': range_from,
                'rangeto_string': range_to,
                'outputformat': 'json',
                'useUTF8': 'true',
                'useISO8601': 'true'
            }
            
            # print(f"📞 Fetching OptiDrive score for: {driver_name_in_webfleet}")
            # print(f"   Date range: {range_from} to {range_to}")
            
            optidrive_response = requests.get(
                self.base_url,
                params=optidrive_params,
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=10
            )
            
            if optidrive_response.status_code != 200:
                print(f"❌ OptiDrive API error: Status {optidrive_response.status_code}")
                return None
            
            optidrive_data = optidrive_response.json()
            
            if not optidrive_data or not isinstance(optidrive_data, list):
                print(f"⚠️ No OptiDrive data returned")
                return None
            
            # STEP 4: Match by driver name in OptiDrive results
            for driver in optidrive_data:
                if not isinstance(driver, dict):
                    continue
                
                optidrive_name = driver.get('drivername', '').strip().lower()
                
                # Try exact match
                if optidrive_name == driver_name_in_webfleet.strip().lower():
                    optidrive = driver.get('optidrive_indicator', 0)
                    try:
                        optidrive = float(optidrive)
                    except (ValueError, TypeError):
                        optidrive = 0
                    
                    # print(f"✓ OptiDrive score: {optidrive}")
                    return optidrive
            
            print(f"⚠️ No OptiDrive data found for driver: {driver_name_in_webfleet}")
            return None
            
        except Exception as e:
            print(f"❌ Error fetching Webfleet data: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_driving_score(self, driver_name):
        """
        Get driving score for a specific driver by name
        Returns the optidrive_indicator (0-1 scale, where 1 is perfect)
        
        NOTE: This method is DEPRECATED - use get_driver_data_by_email() instead
        Name matching is less reliable due to formatting variations
        """
        try:
            # Clean the driver name - remove area codes like (IG8), (NW10), etc.
            clean_name = driver_name.split('(')[0].strip()
            
            # Get date range (last 7 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Format dates as YYYYMMDD
            range_from = start_date.strftime('%Y%m%d')
            range_to = end_date.strftime('%Y%m%d')
            
            # Prepare API parameters
            params = {
                'account': self.account,
                'apikey': self.api_key,
                'lang': 'en',
                'action': 'showOptiDriveIndicator',
                'rangefrom_string': range_from,
                'rangeto_string': range_to,
                'outputformat': 'json',
                'useUTF8': 'true',
                'useISO8601': 'true'
            }
            
            print(f"📞 Calling Webfleet API for driver: {driver_name}")
            print(f"   Cleaned name for search: {clean_name}")
            print(f"   Date range: {range_from} to {range_to}")
            
            # Make API request with Basic Auth
            response = requests.get(
                self.base_url,
                params=params,
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Webfleet API error: Status {response.status_code}")
                return None
            
            # Parse JSON response
            data = response.json()
            
            # CRITICAL FIX: Check if data is valid
            if not data:
                print(f"⚠️ No data returned from Webfleet API")
                return None
            
            # CRITICAL FIX: Check if data is a list and not empty
            if not isinstance(data, list):
                print(f"⚠️ Unexpected data format from Webfleet API: {type(data)}")
                return None
            
            # CRITICAL FIX: Filter out non-dictionary items
            valid_drivers = [item for item in data if isinstance(item, dict)]
            
            if not valid_drivers:
                # print(f"⚠️ No valid driver data found in Webfleet response")
                return None
            
            # Search for driver by name (using cleaned name)
            # Try exact match first
            for driver in valid_drivers:
                driver_name_api = driver.get('drivername', '').strip().lower()
                if driver_name_api == clean_name.strip().lower():
                    optidrive = driver.get('optidrive_indicator', 0)
                    # Convert to float if it's a string
                    try:
                        optidrive = float(optidrive)
                    except (ValueError, TypeError):
                        optidrive = 0
                    # print(f"✓ Found driver: {driver.get('drivername')}, OptiDrive: {optidrive}")
                    return optidrive
            
            # Try partial match (in case of name variations)
            name_parts = clean_name.lower().split()
            for driver in valid_drivers:
                driver_name_api = driver.get('drivername', '').strip().lower()
                # Check if all name parts are in the driver name
                if all(part in driver_name_api for part in name_parts):
                    optidrive = driver.get('optidrive_indicator', 0)
                    # Convert to float if it's a string
                    try:
                        optidrive = float(optidrive)
                    except (ValueError, TypeError):
                        optidrive = 0
                    # print(f"✓ Found driver (partial match): {driver.get('drivername')}, OptiDrive: {optidrive}")
                    return optidrive
            
            # print(f"⚠ Driver '{clean_name}' not found in {len(valid_drivers)} valid driver records")
            return None
            
        except Exception as e:
            # print(f"❌ Error fetching Webfleet data: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_vehicle_locations(self):
        """
        Get current locations for ALL vehicles/drivers in one batch call
        Returns: Dictionary mapping engineer NAME to postcode (matching Red Flags logic)
        Example: {'John Smith': 'SW1A 1AA', 'Jane Doe': 'NW10 5RT'}
        
        This matches the Red Flags implementation for consistency
        """
        try:
            print(f"📍 Fetching ALL vehicle locations from Webfleet (batch)")
            
            # Use showObjectReportExtern to get all vehicles with positions
            vehicle_params = {
                'account': self.account,
                'username': self.username,
                'password': self.password,
                'apikey': self.api_key,
                'lang': 'en',
                'outputformat': 'json',
                'action': 'showObjectReportExtern'
            }
            
            vehicle_response = requests.get(
                self.base_url,
                params=vehicle_params,
                timeout=30
            )
            
            if vehicle_response.status_code != 200:
                print(f"❌ Webfleet API error: Status {vehicle_response.status_code}")
                return {}
            
            vehicle_data = vehicle_response.json()
            
            if not vehicle_data or not isinstance(vehicle_data, list):
                print(f"⚠️ No valid vehicle data returned")
                return {}
            
            print(f"   Found {len(vehicle_data)} vehicles")
            
            # Build map: engineer_name -> postcode
            engineer_to_postcode = {}
            
            for vehicle in vehicle_data:
                if not isinstance(vehicle, dict):
                    continue
                
                # Parse objectname: "ABC123 - John Smith - Electrical"
                object_name = vehicle.get('objectname', '')
                parts = object_name.split(' - ')
                
                # Extract engineer name (middle part)
                engineer_name = parts[1].strip() if len(parts) > 1 else vehicle.get('drivername', '').strip()
                
                # Get address and extract postcode
                address = vehicle.get('postext', '').strip()
                
                if engineer_name and engineer_name != 'Unknown' and address:
                    # Extract postcode from address
                    postcode = self._extract_postcode_from_address(address)
                    
                    if postcode:
                        # Normalize engineer name (remove area codes like (IG8), (NW10))
                        clean_engineer_name = engineer_name.split('(')[0].strip()
                        engineer_to_postcode[clean_engineer_name] = postcode
                        print(f"   ✓ {clean_engineer_name} -> {postcode}")
            
            print(f"📍 Successfully mapped {len(engineer_to_postcode)} engineer locations")
            return engineer_to_postcode
        
        except Exception as e:
            print(f"❌ Error fetching vehicle locations: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _extract_postcode_from_address(self, address):
        """
        Extract UK postcode from address string
        UK postcode format: AA9A 9AA, A9A 9AA, A9 9AA, A99 9AA, AA9 9AA, AA99 9AA
        Examples: SW1A 1AA, E1 6AN, EC1A 1BB
        """
        # UK postcode regex pattern
        # Matches: SW1A 1AA, E1 6AN, EC1A 1BB, etc.
        postcode_pattern = r'([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})'
        
        match = re.search(postcode_pattern, address.upper())
        
        if match:
            postcode = match.group(1).strip()
            # Ensure space in postcode (SW1A1AA -> SW1A 1AA)
            if ' ' not in postcode and len(postcode) > 3:
                postcode = postcode[:-3] + ' ' + postcode[-3:]
            return postcode
        
        return None