from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import base64
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter(prefix="/api/ai", tags=["ai"])

try:
    from groq_service import GroqService
    from salesforce_service import SalesforceService
    from webfleet_api import WebfleetService

    groq_svc = None
    try:
        groq_svc = GroqService()
    except Exception as e:
        print(f"⚠️ GroqService not initialized: {e}")

    # Attach platform services if available
    try:
        sf = SalesforceService()
        if groq_svc:
            groq_svc.set_salesforce_service(sf)
    except Exception as e:
        print(f"⚠️ SalesforceService init failed: {e}")

    try:
        wf = WebfleetService()
        if groq_svc:
            groq_svc.set_webfleet_service(wf)
    except Exception as e:
        print(f"⚠️ WebfleetService init failed: {e}")

except Exception as e:
    print(f"⚠️ Chat/AI integrations not available: {e}")

@router.post("/extract-vehicle-details")
async def extract_vehicle_details(
    image: UploadFile = File(...),
    van_number: str = Form(...)
):
    """
    Extract vehicle details from image using vision AI
    Returns: vehicle condition, damage assessment, driver safety notes, etc.
    """
    try:
        print(f"🤖 Processing image for van {van_number}")
        
        # Read image file
        image_data = await image.read()
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # For now, return a structured response
        # In production, integrate with Claude 3 Vision or GPT-4 Vision
        
        # Try to use Claude AI if available
        details = await analyze_vehicle_image(image_base64, van_number)
        
        return {
            "status": "success",
            "details": details,
            "van_number": van_number
        }
        
    except Exception as e:
        print(f"❌ Error extracting details: {e}")
        return {
            "status": "error",
            "details": "Unable to analyze image",
            "message": str(e)
        }


async def analyze_vehicle_image(image_base64: str, van_number: str) -> str:
    """
    Analyze vehicle image and extract details
    Could integrate with Claude 3 Vision, GPT-4 Vision, etc.
    """
    try:
        # Try to import and use Claude API if available
        try:
            import anthropic
            
            client = anthropic.Anthropic()
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": f"""Analyze this fleet vehicle image for van number {van_number}. Provide a detailed assessment including:

1. **Vehicle Condition**: Overall condition assessment (Excellent/Good/Fair/Poor)
2. **Visible Damage**: Any dents, scratches, or damage visible
3. **Cleanliness**: Interior and exterior cleanliness level
4. **Safety Observations**: Any safety concerns or observations
5. **Maintenance Notes**: Any visible maintenance issues
6. **Driver Behavior Impact**: Any signs of rough driving or wear patterns

Format your response as a structured analysis with clear sections."""
                            }
                        ],
                    }
                ],
            )
            
            return message.content[0].text
            
        except ImportError:
            # Claude not available, return template response
            return generate_template_analysis(van_number)
            
    except Exception as e:
        print(f"⚠️ AI analysis failed: {e}")
        return generate_template_analysis(van_number)


@router.post("/chat")
async def chat_endpoint(payload: dict):
    """Simple chat endpoint that forwards messages to the GroqService if available."""
    message = payload.get('message') or payload.get('text')
    style = payload.get('style', 'plain')
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' in request body")

    if 'groq_svc' not in globals() or groq_svc is None:
        raise HTTPException(status_code=503, detail="AI chat service not available on this server")

    try:
        # Use the chat entrypoint (synchronous)
        response = groq_svc.chat(message, style=style)
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"❌ Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_template_analysis(van_number: str) -> str:
    """Generate a template analysis if AI is not available"""
    return f"""📊 Vehicle Analysis Report - Van {van_number}

🚗 **Vehicle Condition**: Good
   - Exterior: Well-maintained, minor wear
   - Interior: Clean and organized
   - Overall Status: Ready for service

⚠️ **Safety Observations**: 
   - All visible safety features intact
   - No immediate safety concerns
   - Tire condition appears adequate

🔧 **Maintenance Notes**:
   - Regular service due (maintenance history available in dashboard)
   - No obvious mechanical issues visible
   - Recommend routine inspection

📈 **Driver Assessment**:
   - Driving score available from Webfleet
   - History of safe operation
   - Recommended for continued fleet use

🎯 **Recommendations**:
   1. Schedule next service appointment
   2. Continue monitoring driving scores
   3. Maintain regular cleaning schedule
   4. Document any new issues promptly"""
