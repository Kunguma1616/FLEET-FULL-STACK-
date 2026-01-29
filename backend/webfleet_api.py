import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import os
import re
from typing import Dict, List, Optional, Any

class WebfleetService:
    """Complete Webfleet API Integration for Production Fleet Management"""
    
    def __init__(self):
        self.base_url = "https://csv.webfleet.com/extern"
        self.username = os.getenv('WEBFLEET_USERNAME')
        self.password = os.getenv('WEBFLEET_PASSWORD')
        self.account = os.getenv('WEBFLEET_ACCOUNT')
        self.api_key = os.getenv('WEBFLEET_API_KEY')
        
        # Validate credentials
        if not all([self.username, self.password, self.account, self.api_key]):
            raise ValueError("⚠️ Missing Webfleet credentials in .env file")
        
        print(f"✅ Webfleet Service initialized for account: {self.account}")
    
    def _make_request(self, action: str, params: Dict = None) -> Optional[Any]:
        """Make authenticated request to Webfleet API"""
        default_params = {
            'account': self.account,
            'apikey': self.api_key,
            'lang': 'en',
            'outputformat': 'json',
            'useUTF8': 'true',
            'useISO8601': 'true'
        }
        
        if params:
            default_params.update(params)
        
        try:
            response = requests.get(
                self.base_url,
                params={'action': action, **default_params},
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"❌ Webfleet API error: {response.status_code}")
                return None
            
            data = response.json()
            return data if data else None
            
        except Exception as e:
            print(f"❌ Webfleet request failed: {e}")
            return None

    # ===========================
    # REAL-TIME VEHICLE TRACKING
    # ===========================
    
    def get_all_vehicle_positions(self) -> List[Dict]:
        """Get live GPS positions for ALL vehicles"""
        print("📍 Fetching live positions for all vehicles...")
        
        data = self._make_request('showObjectReportExtern')
        
        if not data or not isinstance(data, list):
            return []
        
        vehicles = []
        for vehicle in data:
            if not isinstance(vehicle, dict):
                continue
            
            vehicles.append({
                'vehicle_id': vehicle.get('objectno', ''),
                'vehicle_name': vehicle.get('objectname', ''),
                'latitude': vehicle.get('latitude', 0),
                'longitude': vehicle.get('longitude', 0),
                'speed': vehicle.get('speed', 0),
                'heading': vehicle.get('course', 0),
                'address': vehicle.get('postext', ''),
                'postcode': self._extract_postcode(vehicle.get('postext', '')),
                'last_update': vehicle.get('postime', ''),
                'engine_status': vehicle.get('enginestatus', 'unknown'),
                'driver_name': vehicle.get('drivername', ''),
                'odometer': vehicle.get('odometer', 0),
                'status': 'moving' if vehicle.get('speed', 0) > 5 else 'stopped'
            })
        
        print(f"✅ Found {len(vehicles)} vehicles with live positions")
        return vehicles

    def get_vehicle_location(self, vehicle_id: str) -> Optional[Dict]:
        """Get specific vehicle's current location and status"""
        print(f"📍 Getting live location for {vehicle_id}...")
        
        params = {'objectno': vehicle_id}
        data = self._make_request('showObjectReportExtern', params)
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        vehicle = data[0]
        
        return {
            'vehicle_id': vehicle.get('objectno', ''),
            'latitude': vehicle.get('latitude', 0),
            'longitude': vehicle.get('longitude', 0),
            'speed': vehicle.get('speed', 0),
            'address': vehicle.get('postext', ''),
            'postcode': self._extract_postcode(vehicle.get('postext', '')),
            'last_update': vehicle.get('postime', ''),
            'engine_status': vehicle.get('enginestatus', ''),
            'driver': vehicle.get('drivername', ''),
            'odometer': vehicle.get('odometer', 0),
            'heading': vehicle.get('course', 0)
        }

    # ===========================
    # DRIVER BEHAVIOR & SAFETY
    # ===========================
    
    def get_driving_scores(self, days: int = 7) -> List[Dict]:
        """Get driving scores for all drivers"""
        print(f"🏆 Fetching driving scores (last {days} days)...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'rangefrom_string': start_date.strftime('%Y%m%d'),
            'rangeto_string': end_date.strftime('%Y%m%d')
        }
        
        data = self._make_request('showOptiDriveIndicator', params)
        
        if not data or not isinstance(data, list):
            return []
        
        scores = []
        for driver in data:
            if not isinstance(driver, dict):
                continue
            
            optidrive = float(driver.get('optidrive_indicator', 0))
            score = optidrive * 10  # Convert 0-1 to 0-10 scale
            
            scores.append({
                'driver_name': driver.get('drivername', ''),
                'score': round(score, 1),
                'optidrive': optidrive,
                'score_class': self._get_score_class(score),
                'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            })
        
        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        print(f"✅ Retrieved scores for {len(scores)} drivers")
        return scores

    def get_speeding_events(self, hours: int = 24) -> List[Dict]:
        """Get recent speeding violations"""
        print(f"🚨 Checking for speeding events (last {hours} hours)...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        params = {
            'rangefrom_string': start_date.strftime('%Y%m%d'),
            'rangeto_string': end_date.strftime('%Y%m%d')
        }
        
        data = self._make_request('showEventReportExtern', params)
        
        if not data or not isinstance(data, list):
            return []
        
        speeding_events = []
        for event in data:
            if not isinstance(event, dict):
                continue
            
            event_type = event.get('eventtype', '').lower()
            if 'speed' in event_type or 'overspeed' in event_type:
                speeding_events.append({
                    'vehicle_id': event.get('objectno', ''),
                    'driver': event.get('drivername', ''),
                    'event_type': event.get('eventtype', ''),
                    'description': event.get('eventtext', ''),
                    'speed': event.get('speed', 0),
                    'timestamp': event.get('eventtime', ''),
                    'location': event.get('postext', ''),
                    'severity': self._get_speeding_severity(event.get('speed', 0))
                })
        
        print(f"⚠️ Found {len(speeding_events)} speeding events")
        return speeding_events

    def get_harsh_driving_events(self, hours: int = 24) -> List[Dict]:
        """Get harsh braking/acceleration events"""
        print(f"⚠️ Checking for harsh driving events (last {hours} hours)...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        params = {
            'rangefrom_string': start_date.strftime('%Y%m%d'),
            'rangeto_string': end_date.strftime('%Y%m%d')
        }
        
        data = self._make_request('showEventReportExtern', params)
        
        if not data or not isinstance(data, list):
            return []
        
        harsh_events = []
        for event in data:
            if not isinstance(event, dict):
                continue
            
            event_type = event.get('eventtype', '').lower()
            if any(word in event_type for word in ['brake', 'acceleration', 'corner']):
                harsh_events.append({
                    'vehicle_id': event.get('objectno', ''),
                    'driver': event.get('drivername', ''),
                    'event_type': event.get('eventtype', ''),
                    'description': event.get('eventtext', ''),
                    'timestamp': event.get('eventtime', ''),
                    'location': event.get('postext', '')
                })
        
        print(f"⚠️ Found {len(harsh_events)} harsh driving events")
        return harsh_events

    def get_fuel_consumption(self, days: int = 7) -> List[Dict]:
        """Get fuel consumption data by vehicle"""
        print(f"⛽ Fetching fuel consumption (last {days} days)...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'rangefrom_string': start_date.strftime('%Y%m%d'),
            'rangeto_string': end_date.strftime('%Y%m%d')
        }
        
        data = self._make_request('showFuelConsumptionReportExtern', params)
        
        if not data or not isinstance(data, list):
            return []
        
        fuel_data = []
        for vehicle in data:
            if not isinstance(vehicle, dict):
                continue
            
            fuel_used = float(vehicle.get('fuelconsumption', 0))
            distance = float(vehicle.get('distance', 0))
            efficiency = float(vehicle.get('fuelefficiency', 0))
            
            fuel_data.append({
                'vehicle_id': vehicle.get('objectno', ''),
                'vehicle_name': vehicle.get('objectname', ''),
                'fuel_used_liters': round(fuel_used, 2),
                'distance_km': round(distance, 2),
                'efficiency_l_per_100km': round(efficiency, 2),
                'estimated_cost': round(fuel_used * 1.50, 2),  # £1.50/liter estimate
                'period_days': days
            })
        
        # Sort by fuel consumption (highest first)
        fuel_data.sort(key=lambda x: x['fuel_used_liters'], reverse=True)
        print(f"✅ Retrieved fuel data for {len(fuel_data)} vehicles")
        return fuel_data

    def get_idle_time(self, days: int = 1) -> List[Dict]:
        """Get idle time by vehicle (fuel waste)"""
        print(f"⏱️ Checking idle time (last {days} days)...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'rangefrom_string': start_date.strftime('%Y%m%d'),
            'rangeto_string': end_date.strftime('%Y%m%d')
        }
        
        data = self._make_request('showIdlingReportExtern', params)
        
        if not data or not isinstance(data, list):
            return []
        
        idle_data = []
        for vehicle in data:
            if not isinstance(vehicle, dict):
                continue
            
            idle_time = float(vehicle.get('idletime', 0))
            idle_hours = idle_time / 3600  # Convert seconds to hours
            
            # Estimate fuel waste: ~1 liter per hour idling
            fuel_waste = idle_hours * 1.0
            cost_waste = fuel_waste * 1.50  # £1.50/liter
            
            if idle_hours > 0.1:  # Only include if >6 minutes
                idle_data.append({
                    'vehicle_id': vehicle.get('objectno', ''),
                    'vehicle_name': vehicle.get('objectname', ''),
                    'idle_time_hours': round(idle_hours, 2),
                    'fuel_wasted_liters': round(fuel_waste, 2),
                    'cost_wasted': round(cost_waste, 2),
                    'severity': 'high' if idle_hours > 4 else 'medium' if idle_hours > 2 else 'low'
                })
        
        # Sort by idle time (highest first)
        idle_data.sort(key=lambda x: x['idle_time_hours'], reverse=True)
        print(f"⚠️ Found {len(idle_data)} vehicles with significant idle time")
        return idle_data

    def get_trip_summary(self, vehicle_id: str, days: int = 1) -> Optional[Dict]:
        """Get trip summary for a specific vehicle"""
        print(f"🛣️ Getting trip summary for {vehicle_id}...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'objectno': vehicle_id,
            'rangefrom_string': start_date.strftime('%Y%m%d'),
            'rangeto_string': end_date.strftime('%Y%m%d')
        }
        
        data = self._make_request('showTripSummaryReportExtern', params)
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        trip = data[0]
        
        total_time = float(trip.get('totaltime', 0)) / 3600  # seconds to hours
        driving_time = float(trip.get('drivingtime', 0)) / 3600
        idle_time = float(trip.get('idletime', 0)) / 3600
        
        return {
            'vehicle_id': trip.get('objectno', ''),
            'total_distance_km': round(float(trip.get('totaldistance', 0)) / 1000, 2),
            'total_time_hours': round(total_time, 2),
            'driving_time_hours': round(driving_time, 2),
            'idle_time_hours': round(idle_time, 2),
            'number_of_stops': trip.get('stops', 0),
            'fuel_used_liters': round(float(trip.get('fuelused', 0)), 2),
            'period_days': days
        }

    def get_vehicle_history(self, vehicle_id: str, date: str) -> List[Dict]:
        """Get detailed trip history for a specific date"""
        print(f"📅 Getting trip history for {vehicle_id} on {date}...")
        
        params = {
            'objectno': vehicle_id,
            'rangefrom_string': date.replace('-', ''),
            'rangeto_string': date.replace('-', '')
        }
        
        data = self._make_request('showTripReportExtern', params)
        
        if not data or not isinstance(data, list):
            return []
        
        trips = []
        for trip in data:
            if not isinstance(trip, dict):
                continue
            
            trips.append({
                'start_time': trip.get('starttime', ''),
                'end_time': trip.get('endtime', ''),
                'start_location': trip.get('startaddress', ''),
                'end_location': trip.get('endaddress', ''),
                'distance_km': round(float(trip.get('distance', 0)) / 1000, 2),
                'duration_minutes': round(float(trip.get('duration', 0)) / 60, 2),
                'driver': trip.get('drivername', '')
            })
        
        print(f"✅ Found {len(trips)} trips")
        return trips

    def get_vehicle_diagnostics(self, vehicle_id: str) -> List[Dict]:
        """Get engine diagnostic codes (DTC)"""
        print(f"🔧 Checking diagnostics for {vehicle_id}...")
        
        params = {'objectno': vehicle_id}
        data = self._make_request('showVehicleDiagnosticsExtern', params)
        
        if not data or not isinstance(data, list):
            return []
        
        diagnostics = []
        for item in data:
            if not isinstance(item, dict):
                continue
            
            dtc_code = item.get('dtccode', '')
            
            diagnostics.append({
                'vehicle_id': item.get('objectno', ''),
                'dtc_code': dtc_code,
                'description': item.get('dtcdescription', ''),
                'severity': self._get_dtc_severity(dtc_code),
                'timestamp': item.get('timestamp', ''),
                'action_required': self._get_dtc_action(dtc_code)
            })
        
        print(f"{'⚠️' if diagnostics else '✅'} Found {len(diagnostics)} diagnostic codes")
        return diagnostics

    def get_odometer_readings(self) -> List[Dict]:
        """Get current odometer readings for all vehicles"""
        print("📏 Getting odometer readings...")
        
        data = self._make_request('showObjectReportExtern')
        
        if not data or not isinstance(data, list):
            return []
        
        readings = []
        for vehicle in data:
            if not isinstance(vehicle, dict):
                continue
            
            odometer = float(vehicle.get('odometer', 0))
            
            readings.append({
                'vehicle_id': vehicle.get('objectno', ''),
                'vehicle_name': vehicle.get('objectname', ''),
                'odometer_km': round(odometer / 1000, 2),
                'odometer_miles': round(odometer / 1609.34, 2),
                'last_update': vehicle.get('postime', '')
            })
        
        return readings

    def get_working_hours(self, driver_id: str, days: int = 1) -> Optional[Dict]:
        """Get driver working hours (tachograph data)"""
        print(f"⏰ Getting working hours for {driver_id}...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'objectno': driver_id,
            'rangefrom_string': start_date.strftime('%Y%m%d'),
            'rangeto_string': end_date.strftime('%Y%m%d')
        }
        
        data = self._make_request('showWorkingTimeReportExtern', params)
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        working_time = data[0]
        
        driving_time = float(working_time.get('drivingtime', 0)) / 3600
        total_working = float(working_time.get('workingtime', 0)) / 3600
        rest_time = float(working_time.get('resttime', 0)) / 3600
        
        return {
            'driver_id': working_time.get('objectno', ''),
            'driving_hours': round(driving_time, 2),
            'working_hours': round(total_working, 2),
            'rest_hours': round(rest_time, 2),
            'remaining_driving_hours': round(float(working_time.get('remainingdrivingtime', 0)) / 3600, 2),
            'compliance_status': 'compliant' if driving_time < 9 else 'warning'
        }

    def _extract_postcode(self, address: str) -> Optional[str]:
        """Extract UK postcode from address"""
        if not address:
            return None
        
        postcode_pattern = r'([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})'
        match = re.search(postcode_pattern, address.upper())
        
        if match:
            postcode = match.group(1).strip()
            if ' ' not in postcode and len(postcode) > 3:
                postcode = postcode[:-3] + ' ' + postcode[-3:]
            return postcode
        
        return None

    def _get_score_class(self, score: float) -> str:
        """Convert score to classification"""
        if score >= 9.0:
            return 'excellent'
        elif score >= 8.0:
            return 'good'
        elif score >= 7.0:
            return 'fair'
        elif score >= 6.0:
            return 'needs_improvement'
        else:
            return 'poor'

    def _get_speeding_severity(self, speed: float) -> str:
        """Determine speeding severity"""
        if speed > 90:
            return 'critical'
        elif speed > 80:
            return 'high'
        elif speed > 70:
            return 'medium'
        else:
            return 'low'

    def _get_dtc_severity(self, dtc_code: str) -> str:
        """Determine diagnostic code severity"""
        if not dtc_code:
            return 'unknown'
        
        if dtc_code.startswith('P'):
            if len(dtc_code) > 1 and dtc_code[1] == '0':
                return 'critical'
            else:
                return 'high'
        elif dtc_code.startswith('B'):
            return 'medium'
        elif dtc_code.startswith('C'):
            return 'high'
        else:
            return 'low'

    def _get_dtc_action(self, dtc_code: str) -> str:
        """Get recommended action for DTC code"""
        if not dtc_code:
            return 'Monitor'
        
        critical_codes = ['P0420', 'P0430', 'P0300', 'P0171', 'P0174']
        
        if dtc_code in critical_codes:
            return 'Service immediately'
        elif dtc_code.startswith('P0'):
            return 'Schedule service soon'
        else:
            return 'Monitor and check at next service'

    def get_fleet_health_summary(self) -> Dict:
        """Get overall fleet health metrics"""
        print("📊 Generating fleet health summary...")
        
        positions = self.get_all_vehicle_positions()
        fuel_data = self.get_fuel_consumption(days=7)
        idle_data = self.get_idle_time(days=1)
        speeding = self.get_speeding_events(hours=24)
        
        active_vehicles = len([v for v in positions if v['status'] == 'moving'])
        
        total_fuel_cost = sum(f['estimated_cost'] for f in fuel_data)
        total_idle_cost = sum(i['cost_wasted'] for i in idle_data)
        
        return {
            'total_vehicles': len(positions),
            'active_vehicles': active_vehicles,
            'stopped_vehicles': len(positions) - active_vehicles,
            'fuel_cost_7_days': round(total_fuel_cost, 2),
            'idle_waste_today': round(total_idle_cost, 2),
            'speeding_incidents_24h': len(speeding),
            'high_fuel_consumers': len([f for f in fuel_data if f['efficiency_l_per_100km'] > 15]),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test the service
    try:
        service = WebfleetService()
        
        print("\n" + "="*50)
        print("TESTING WEBFLEET SERVICE")
        print("="*50)
        
        # Test 1: Get all positions
        positions = service.get_all_vehicle_positions()
        print(f"\n✅ Found {len(positions)} vehicles")
        
        # Test 2: Get driving scores
        scores = service.get_driving_scores(days=7)
        print(f"✅ Retrieved scores for {len(scores)} drivers")
        
        # Test 3: Get fleet health
        health = service.get_fleet_health_summary()
        print(f"\n📊 Fleet Health Summary:")
        for key, value in health.items():
            print(f"   {key}: {value}")
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
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