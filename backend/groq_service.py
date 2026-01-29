from groq import Groq
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re

class GroqService:
    """Professional AI with structured output for all queries"""
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.groq_client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.current_date = datetime.now()
        
        self.salesforce_service = None
        self.webfleet_service = None
        
        print("✅ Professional AI Service initialized")
    
    def set_salesforce_service(self, sf_service):
        self.salesforce_service = sf_service
        print("✅ Salesforce connected")
    
    def set_webfleet_service(self, wf_service):
        self.webfleet_service = wf_service
        print("✅ Webfleet connected")
    
    def classify_intent_and_execute(self, user_message: str, conversation_history: List = None) -> Dict:
        """Smart intent classification"""
        
        message_lower = user_message.lower()
        
        # VEHICLE HEALTH
        if any(word in message_lower for word in ['health', 'status', 'check', 'info']):
            vehicle_id = self._extract_vehicle_id(user_message)
            if vehicle_id:
                return self._execute_intent('get_vehicle_health', {'vehicle_id': vehicle_id}, user_message)
        
        # FLEET HEALTH
        if 'fleet' in message_lower:
            vehicle_id = self._extract_vehicle_id(user_message)
            if vehicle_id:
                return self._execute_intent('get_vehicle_health', {'vehicle_id': vehicle_id}, user_message)
            else:
                return self._execute_intent('get_fleet_health', {}, user_message)
        
        # MAINTENANCE
        if any(phrase in message_lower for phrase in ['maintenance', 'service due', 'need service']):
            return self._execute_intent('get_maintenance_due', {}, user_message)
        
        # DRIVING SCORES
        if 'driving score' in message_lower or 'driver performance' in message_lower:
            return self._execute_intent('get_driving_scores', {'days': 7}, user_message)
        
        # FUEL
        if 'fuel' in message_lower:
            days = 7 if 'week' in message_lower else 1
            return self._execute_intent('get_fuel_data', {'days': days}, user_message)
        
        # IDLE
        if 'idle' in message_lower:
            return self._execute_intent('get_idle_waste', {'days': 1}, user_message)
        
        # SPEEDING
        if 'speeding' in message_lower or 'speed' in message_lower:
            return self._execute_intent('get_speeding_alerts', {'hours': 24}, user_message)
        
        # LOCATION
        if any(word in message_lower for word in ['where is', 'location']):
            vehicle_id = self._extract_vehicle_id(user_message)
            if vehicle_id:
                return self._execute_intent('get_live_location', {'vehicle_id': vehicle_id}, user_message)
        
        if 'all vehicle' in message_lower or 'show vehicles' in message_lower or 'vehicle positions' in message_lower:
            return self._execute_intent('get_all_positions', {}, user_message)
        
        # COUNT
        if 'how many' in message_lower:
            return self._execute_intent('get_vehicle_count', {}, user_message)
        
        return {
            'intent': {'intent': 'help'},
            'data': None,
            'error': 'Try: "VEH-00330 health", "driving scores", "maintenance due", "fuel consumption"'
        }
    
    def _execute_intent(self, intent: str, parameters: Dict, user_message: str) -> Dict:
        """Execute with proper error handling"""
        
        print(f"⚡ Executing: {intent}")
        
        # VEHICLE HEALTH
        if intent == 'get_vehicle_health':
            vehicle_id = parameters.get('vehicle_id')
            health_data = {}
            
            if self.salesforce_service:
                try:
                    vehicle = self.salesforce_service.get_vehicle_by_identifier(vehicle_id)
                    if vehicle:
                        health_data['vehicle_info'] = vehicle
                    
                    maintenance = self.salesforce_service.get_vehicle_maintenance(vehicle_id)
                    if maintenance:
                        health_data['maintenance'] = maintenance[0] if maintenance else None
                    
                    allocations = self.salesforce_service.get_vehicle_allocations(vehicle_id)
                    if allocations:
                        health_data['allocation'] = allocations[0] if allocations else None
                except Exception as e:
                    print(f"⚠️ Salesforce error: {e}")
            
            if self.webfleet_service:
                try:
                    location = self.webfleet_service.get_vehicle_location(vehicle_id)
                    if location:
                        health_data['live_location'] = location
                    
                    trip = self.webfleet_service.get_trip_summary(vehicle_id, days=7)
                    if trip:
                        health_data['trip_summary'] = trip
                except Exception as e:
                    print(f"⚠️ Webfleet error: {e}")
            
            return {
                'intent': {'intent': intent, 'confidence': 0.95},
                'data': health_data if health_data else None,
                'source': 'combined',
                'context': 'vehicle_health',
                'vehicle_id': vehicle_id
            }
        
        # MAINTENANCE
        elif intent == 'get_maintenance_due':
            if self.salesforce_service:
                maintenance = self.salesforce_service.get_vehicle_maintenance()
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': maintenance if maintenance else [],
                    'source': 'salesforce',
                    'context': 'maintenance_schedule',
                    'count': len(maintenance) if maintenance else 0
                }
        
        # DRIVING SCORES
        elif intent == 'get_driving_scores':
            if self.webfleet_service:
                scores = self.webfleet_service.get_driving_scores(days=7)
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': scores if scores else [],
                    'source': 'webfleet',
                    'context': 'driver_performance',
                    'count': len(scores) if scores else 0
                }
        
        # FUEL
        elif intent == 'get_fuel_data':
            days = parameters.get('days', 7)
            if self.webfleet_service:
                fuel = self.webfleet_service.get_fuel_consumption(days=days)
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': fuel if fuel else [],
                    'source': 'webfleet',
                    'context': 'fuel_analysis',
                    'period_days': days,
                    'count': len(fuel) if fuel else 0
                }
        
        # IDLE
        elif intent == 'get_idle_waste':
            if self.webfleet_service:
                idle = self.webfleet_service.get_idle_time(days=1)
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': idle if idle else [],
                    'source': 'webfleet',
                    'context': 'idle_waste',
                    'count': len(idle) if idle else 0
                }
        
        # SPEEDING
        elif intent == 'get_speeding_alerts':
            if self.webfleet_service:
                speeding = self.webfleet_service.get_speeding_events(hours=24)
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': speeding if speeding else [],
                    'source': 'webfleet',
                    'context': 'safety_violations',
                    'count': len(speeding) if speeding else 0
                }
        
        # ALL POSITIONS
        elif intent == 'get_all_positions':
            if self.webfleet_service:
                positions = self.webfleet_service.get_all_vehicle_positions()
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': positions if positions else [],
                    'source': 'webfleet',
                    'context': 'live_positions',
                    'count': len(positions) if positions else 0
                }
        
        # FLEET HEALTH
        elif intent == 'get_fleet_health':
            if self.webfleet_service:
                health = self.webfleet_service.get_fleet_health_summary()
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': health,
                    'source': 'webfleet',
                    'context': 'fleet_health'
                }
        
        # VEHICLE COUNT
        elif intent == 'get_vehicle_count':
            if self.salesforce_service:
                vehicles = self.salesforce_service.get_all_vehicles()
                return {
                    'intent': {'intent': intent, 'confidence': 0.95},
                    'data': vehicles,
                    'source': 'salesforce',
                    'count': len(vehicles)
                }
        
        return {'intent': {'intent': 'unknown'}, 'data': None}
    
    def generate_natural_response(self, user_message: str, intent_result: Dict) -> str:
        """Generate PROFESSIONAL STRUCTURED output - NO JSON dumps"""
        
        intent = intent_result.get('intent', {}).get('intent', 'unknown')
        data = intent_result.get('data')
        error = intent_result.get('error')
        context = intent_result.get('context', '')
        count = intent_result.get('count', 0)
        
        if error:
            return f"ℹ️ {error}"
        
        if not data or (isinstance(data, list) and len(data) == 0):
            return f"ℹ️ No data available for this query.\n\nPossible reasons:\n• Service temporarily unavailable\n• No matching records\n• Data not yet synced"
        
        date_str = self.current_date.strftime('%B %d, %Y')
        
        try:
            # (Response generation logic... shortened for file)
            # Delegate vehicle health to helper
            if context == 'vehicle_health':
                return self._generate_vehicle_health_response(data, intent_result)

            # Fallback: return a simple summary
            response = f"Date: {date_str}\n\nResults:\n"
            if isinstance(data, list):
                response += f"Found {len(data)} records\n"
            elif isinstance(data, dict):
                for k, v in data.items():
                    response += f"- {k}: {v}\n"
            return response
        except Exception as e:
            print(f"❌ Response generation error: {e}")
            return f"ℹ️ Data retrieved but formatting error occurred."
    
    def chat(self, user_message: str, conversation_history: List = None, *, style: str = 'plain', return_dict: bool = False) -> str:
        intent_result = self.classify_intent_and_execute(user_message, conversation_history)
        response_text = self.generate_natural_response(user_message, intent_result)
        if return_dict:
            return intent_result
        remove_emojis = True if style == 'plain' else False
        remove_ellipsis = True if style == 'plain' else False
        return self._sanitize_to_plain_text(response_text, remove_emojis=remove_emojis, remove_ellipsis=remove_ellipsis)
    
    def _sanitize_to_plain_text(self, text: str, remove_emojis: bool = True, remove_ellipsis: bool = True) -> str:
        if not text:
            return text
        out = text.replace('**', '')
        out = out.replace('\t', ' ')
        out = out.replace('•', '-')
        if remove_ellipsis:
            out = out.replace('...', '')
        if remove_emojis:
            try:
                emoji_pattern = re.compile(
                    '[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF]'
                )
                out = emoji_pattern.sub('', out)
            except re.error:
                for ch in ['🟢','🔴','📍','📅','🏆','🥇','🥈','🥉','💡','🔧','⚠️']:
                    out = out.replace(ch, '')
        out = re.sub(r'\*{2,}', '', out)
        out = re.sub(r'-{3,}', '---', out)
        out = re.sub(r'\n{3,}', '\n\n', out)
        out = '\n'.join(line.rstrip() for line in out.splitlines())
        out = out.strip() + '\n'
        return out
    
    def _generate_vehicle_health_response(self, data: Dict, intent_result: Dict) -> str:
        vehicle_id = intent_result.get('vehicle_id', 'Unknown')
        date_str = self.current_date.strftime('%B %d, %Y')
        response = f"📅 {date_str}\n\n"
        response += f"🚗 **VEHICLE HEALTH REPORT: {vehicle_id}**\n"
        if 'vehicle_info' in data:
            v = data['vehicle_info']
            response += f"- ID: {v.get('Name', 'N/A')}\n"
            response += f"- Registration: {v.get('Reg_No__c', 'N/A')}\n"
        return response
    
    def _extract_vehicle_id(self, text: str) -> Optional[str]:
        match = re.search(r'VEH-\d{3,5}', text.upper())
        return match.group(0) if match else None


if __name__ == "__main__":
    try:
        svc = GroqService()
    except ValueError as e:
        print(f"Initialization error: {e}\nSet the GROQ_API_KEY environment variable to run the interactive demo.")
    else:
        print("✅ Professional AI Service ready — type a question (ctrl-c to exit)")
        try:
            while True:
                user = input('\nUser: ').strip()
                if not user:
                    print('Please enter a question or ctrl-c to exit')
                    continue
                out = svc.chat(user)
                print(f"\nAssistant:\n{out}\n")
        except (KeyboardInterrupt, EOFError):
            print('\nExiting.')
import os
import json
import traceback
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq library not installed. Install with: pip install groq")

from salesforce_service import SalesforceService


class GroqService:
    """
    Intelligent AI service that understands user intent and routes to appropriate Salesforce queries
    Uses few-shot prompting for accurate intent classification
    """

    def __init__(self):
        if not GROQ_AVAILABLE:
            print("⚠️  Groq not available - chat will have limited functionality")
            self.client = None
            return
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️  GROQ_API_KEY not set - chat functionality disabled")
            self.client = None
            return
        
        self.client = Groq(api_key=api_key)
        self.sf = SalesforceService()
        self.conversation_context = {}
        print("✅ Groq service initialized")

    def set_salesforce_service(self, sf_service):
        """Allow external code to attach an existing SalesforceService instance."""
        self.sf = sf_service
        print("✅ GroqService: Salesforce service attached")

    def set_webfleet_service(self, wf_service):
        """Allow external code to attach a Webfleet service instance."""
        self.webfleet = wf_service
        print("✅ GroqService: Webfleet service attached")

    def is_available(self) -> bool:
        """Check if Groq service is available"""
        return self.client is not None

    def classify_intent_and_execute(self, user_question: str, conversation_history: list = None) -> dict:
        """
        Uses few-shot prompting to classify intent, then executes appropriate Salesforce query
        """
        if not self.is_available():
            return {"intent": {"intent": "error"}, "data": [], "count": 0, "error": "Groq service not available"}
        
        try:
            # Extract vehicle context from recent conversation
            last_vehicle = self._extract_vehicle_from_history(conversation_history or [])
            
            # Few-shot prompt for intent classification
            classification_prompt = f"""You are an expert at understanding questions about vehicle fleet management.

Your job: Analyze the user's question and output a JSON object with the intent and parameters.

IMPORTANT CONTEXT:
- Previous vehicle mentioned: {last_vehicle or "None"}
- If user says "it", "this", "that vehicle", use the previous vehicle

=== FEW-SHOT EXAMPLES ===

Example 1:
User: "How many vehicles are there in total"
Output: {{"intent": "count_all_vehicles", "entity": null, "parameters": {{}}}}

Example 2:
User: "Tell me about VEH-439"
Output: {{"intent": "get_vehicle_info", "entity": "VEH-439", "parameters": {{}}}}

Example 3:
User: "What's the lease date for it?"
Context: Previous vehicle was VEH-439
Output: {{"intent": "get_vehicle_lease", "entity": "VEH-439", "parameters": {{}}}}

Example 4:
User: "Who is driving that vehicle?"
Context: Previous vehicle was VEH-439
Output: {{"intent": "get_vehicle_driver", "entity": "VEH-439", "parameters": {{}}}}

Example 5:
User: "Show me the costs for this vehicle"
Context: Previous vehicle was VEH-439
Output: {{"intent": "get_vehicle_costs", "entity": "VEH-439", "parameters": {{}}}}

Example 6:
User: "How many allocated vehicles?"
Output: {{"intent": "count_by_status", "entity": null, "parameters": {{"status": "Allocated"}}}}

Example 7:
User: "List all drivers"
Output: {{"intent": "list_all_drivers", "entity": null, "parameters": {{}}}}

Example 8:
User: "Show spare drainage vans"
Output: {{"intent": "get_spare_vehicles", "entity": null, "parameters": {{"trade_group": "Drainage"}}}}

Example 9:
User: "What vehicles need maintenance?"
Output: {{"intent": "get_maintenance_schedule", "entity": null, "parameters": {{}}}}

Example 10:
User: "Show me vehicles at Croydon depot"
Output: {{"intent": "get_vehicles_by_location", "entity": null, "parameters": {{"location": "Croydon"}}}}

=== AVAILABLE INTENTS ===
- count_all_vehicles: Total number of vehicles
- count_by_status: Count vehicles by status (Allocated, Spare, etc)
- get_vehicle_info: Basic vehicle information
- get_vehicle_lease: Lease/ownership dates
- get_vehicle_driver: Who is driving the vehicle
- get_vehicle_costs: Cost records for vehicle
- get_vehicle_maintenance: Maintenance/MOT/service info
- list_all_drivers: List all drivers with their vehicles
- get_spare_vehicles: Available/spare vehicles
- get_maintenance_schedule: Vehicles needing maintenance
- get_vehicles_by_location: Vehicles at specific depot

=== NOW CLASSIFY THIS ===
User question: "{user_question}"
Previous vehicle context: {last_vehicle or "None"}

Output only valid JSON in this exact format:
{{"intent": "intent_name", "entity": "vehicle_id or null", "parameters": {{}}}}
"""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a precise JSON classifier. Always output valid JSON only."},
                    {"role": "user", "content": classification_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            intent_json = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            intent_json = intent_json.replace("```json", "").replace("```", "").strip()
            intent_data = json.loads(intent_json)
            
            print(f"🎯 Intent: {intent_data['intent']} | Entity: {intent_data.get('entity')}")
            
            # Execute the appropriate Salesforce query
            result = self._execute_intent(intent_data)
            
            return {
                "intent": intent_data,
                "data": result,
                "count": len(result) if isinstance(result, list) else (1 if result else 0)
            }
            
        except Exception as e:
            print(f"❌ Intent classification error: {e}")
            traceback.print_exc()
            return {"intent": {"intent": "error"}, "data": [], "count": 0, "error": str(e)}

    def _extract_vehicle_from_history(self, history: list) -> Optional[str]:
        """Extract the most recent vehicle ID from conversation history"""
        import re
        for msg in reversed(history[-5:]):  # Check last 5 messages
            content = msg.get("content", "")
            veh_match = re.search(r'VEH-\d+', content, re.IGNORECASE)
            if veh_match:
                return veh_match.group(0)
        return None

    def _execute_intent(self, intent_data: dict) -> Any:
        """Route intent to appropriate Salesforce method"""
        intent = intent_data['intent']
        entity = intent_data.get('entity')
        params = intent_data.get('parameters', {})
        
        try:
            # Route to appropriate Salesforce service method
            if intent == 'count_all_vehicles':
                data = self.sf.get_all_vehicles()
                return data
                
            elif intent == 'count_by_status':
                status = params.get('status', 'Allocated')
                return self.sf.get_vehicles_by_status(status)
                
            elif intent == 'get_vehicle_info':
                if entity:
                    vehicle = self.sf.get_vehicle_by_identifier(entity)
                    return [vehicle] if vehicle else []
                return []
                
            elif intent == 'get_vehicle_lease':
                if entity:
                    vehicle = self.sf.get_vehicle_by_identifier(entity)
                    return [vehicle] if vehicle else []
                return []
                
            elif intent == 'get_vehicle_driver':
                if entity:
                    return self.sf.get_vehicle_allocations(entity)
                return []
                
            elif intent == 'get_vehicle_costs':
                return self.sf.get_vehicle_costs(entity, limit=20)
                
            elif intent == 'get_vehicle_maintenance':
                return self.sf.get_vehicle_maintenance(entity)
                
            elif intent == 'list_all_drivers':
                return self.sf.get_vehicle_allocations()
                
            elif intent == 'get_spare_vehicles':
                return self.sf.get_vehicles_by_status('Spare')
                
            elif intent == 'get_maintenance_schedule':
                return self.sf.get_vehicle_maintenance()
                
            elif intent == 'get_vehicles_by_location':
                location = params.get('location')
                if location:
                    return self.sf.get_vehicles_by_location(location)
                return []
                
            else:
                return []
        except Exception as e:
            print(f"❌ Intent execution error: {e}")
            return []

    def generate_natural_response(self, user_question: str, intent_result: dict) -> str:
        """Generate natural language response from data"""
        if not self.is_available():
            return "Chat service temporarily unavailable"
        
        try:
            intent = intent_result.get('intent', {}).get('intent', 'unknown')
            data = intent_result.get('data', [])
            count = intent_result.get('count', 0)
            
            if intent_result.get('error'):
                return f"Error processing request: {intent_result['error']}"
            
            response_prompt = f"""You are a helpful fleet management assistant.

User asked: "{user_question}"
Intent classified as: {intent}
Data retrieved: {count} records

Data: {json.dumps(data[:3], indent=2) if data else "No data found"}

Generate a natural, concise response. Include:
- Direct answer to the question
- Key details from the data (if applicable)
- Be specific with numbers and names

Keep response under 100 words."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a concise, helpful assistant."},
                    {"role": "user", "content": response_prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Response generation error: {e}")
            return f"Found {count} results related to your query."
