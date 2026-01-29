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
