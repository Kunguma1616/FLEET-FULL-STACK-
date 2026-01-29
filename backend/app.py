from fastapi import FastAPI, HTTPException
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import openpyxl
import glob
import re

# Try to import Groq for AI features (optional)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq library not installed. Install with: pip install groq")

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.dashboard import router as dashboard_router
from routes.webfleet import router as webfleet_router
from routes.vehicles import router as vehicles_router
from routes.assets import router as assets_router
from routes.ai import router as ai_router
from routes.chat import router as chat_router
from routes.auth import router as auth_router

# Initialize FastAPI app
app = FastAPI(
    title="Fleet Health Monitor API",
    description="Backend API for fleet management dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://192.168.54.48:5174", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router)
app.include_router(webfleet_router)
app.include_router(vehicles_router)
app.include_router(assets_router)
app.include_router(ai_router)
app.include_router(chat_router)
app.include_router(auth_router)


# ========================================
# 🤖 GROK AI MODEL FOR ANALYSIS
# ========================================

def get_grok_analysis(description: str, context: str = "vehicle") -> str:
    """
    Use Grok model to provide high-level AI analysis
    Supports vehicle descriptions, driver history, maintenance notes, etc.
    """
    if not GROQ_AVAILABLE:
        return "AI analysis unavailable - Groq library not installed. Run: pip install groq"
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ GROQ_API_KEY not set, skipping AI analysis")
            return "AI analysis unavailable - API key not configured"
        
        client = Groq(api_key=api_key)
        
        # Create the prompt based on context
        if context == "vehicle":
            prompt = f"""Provide a brief high-level summary of this vehicle's condition and status based on the description:
            
"{description}"

Keep it concise (2-3 sentences) and focus on key maintenance needs, issues, or positive aspects."""
        
        elif context == "driver_history":
            prompt = f"""Analyze this driver history and provide key insights about the driver's profile:
            
"{description}"

Summarize in 2-3 sentences highlighting tenure, performance patterns, or notable observations."""
        
        else:
            prompt = f"""Provide a brief analysis of: {description}"""
        
        print(f"🤖 Requesting Grok analysis for {context}...")
        
        message = client.messages.create(
            model="grok-2-1212",  # Latest Grok model
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,  # Keep it brief
        )
        
        analysis = message.content[0].text
        print(f"✅ Grok analysis complete: {analysis[:100]}...")
        return analysis
        
    except Exception as e:
        print(f"⚠️ Grok analysis error: {e}")
        return f"Analysis unavailable: {str(e)}"





def is_valid_name(name):
    """
    LENIENT validation - only rejects OBVIOUS garbage/code
    Keeps ALL real human names
    """
    if not name or len(name) < 2:
        return False
    
    # Convert to string and clean
    name = str(name).strip()
    
    # ONLY reject OBVIOUS code/error patterns
    obvious_garbage = [
        'File "',
        'Traceback',
        'apply_stylesheet',
        'self.archive',
        'self.wb',
        'from_tree',
        'super()',
        'cls(**attrib)',
        'self.fills = fills',
        '_convert(',
        'expected_type',
        'seq = self.container',
        'for value in seq',
        'raise TypeError',
        'openpyxl.',
        '.py", line',
        'def __init__',
        '~~~~~~~~^^^',
        '~~~~~~~~~~~~~~~~^',
        '^^^^^^^^^^',
        '~~~~~~~~~~~~~~~~~~~~',
    ]
    
    # Check for obvious garbage
    name_lower = name.lower()
    for pattern in obvious_garbage:
        if pattern.lower() in name_lower:
            return False
    
    # Reject if MOSTLY symbols (>70% not alphanum)
    if len(name) > 0:
        alnum_count = sum(1 for c in name if c.isalnum() or c == ' ' or c == '-')
        if (alnum_count / len(name)) < 0.3:  # Less than 30% normal chars
            return False
    
    # Must have at least one letter
    if not any(c.isalpha() for c in name):
        return False
    
    # That's it! If it passes these simple checks, it's probably a real name
    return True


def find_drivers_file():
    """Auto-find the Drivers CSV/Excel file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    search_patterns = [
        os.path.join(project_root, 'public', 'Drivers_2026-01-28_14-30.csv'),
        os.path.join(project_root, 'public', 'Drivers*.csv'),
        os.path.join(project_root, 'Drivers*.csv'),
        os.path.join(current_dir, 'Drivers*.csv'),
    ]
    
    for pattern in search_patterns:
        if '*' in pattern:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        else:
            if os.path.exists(pattern):
                return pattern
    
    return None


def read_drivers_file_safely(file_path):
    """Read drivers with multiple encoding support"""
    is_csv = file_path.lower().endswith('.csv')
    
    if is_csv:
        encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
        
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip')
                
                # Find real header row if error messages at top
                if len(df) > 0:
                    for idx in range(min(50, len(df))):
                        row_str = ' '.join(df.iloc[idx].astype(str).values)
                        if 'Name' in row_str and ('OptiDrive' in row_str or 'Score' in row_str):
                            df = pd.read_csv(file_path, skiprows=idx, encoding=encoding, on_bad_lines='skip')
                            break
                
                # Clean dataframe
                if len(df) > 0:
                    df = df[df.iloc[:, 0].notna()]
                    return df
                    
            except:
                continue
        
        return None
    else:
        # Excel reading methods
        try:
            return pd.read_excel(file_path, engine='openpyxl')
        except:
            try:
                workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                sheet = workbook.active
                data = list(sheet.iter_rows(values_only=True))
                workbook.close()
                if data and len(data) > 1:
                    return pd.DataFrame(data[1:], columns=data[0])
            except:
                pass
    
    return None


def get_score_class(score):
    """Determine score classification"""
    if score >= 9.0:
        return "excellent"
    elif score >= 8.0:
        return "good"
    elif score >= 7.0:
        return "fair"
    elif score >= 6.0:
        return "needs_improvement"
    else:
        return "poor"


@app.get("/api/drivers/excel")
def get_drivers_from_excel():
    """
    Get CLEAN driver data with aggressive filtering
    """
    try:
        # Find and read file
        file_path = find_drivers_file()
        if file_path is None:
            raise HTTPException(status_code=404, detail="Drivers file not found")
        
        df = read_drivers_file_safely(file_path)
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="Could not read drivers file")
        
        # Auto-detect columns
        name_col = None
        score_col = None
        van_col = None
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if 'name' in col_lower and name_col is None:
                name_col = col
            elif 'optidrive' in col_lower or 'score' in col_lower:
                score_col = col
            elif 'no.' in col_lower or 'van' in col_lower:
                van_col = col
        
        # Process rows with LENIENT filtering
        drivers = []
        rejected_count = 0
        empty_names = 0
        
        print(f"📊 Processing {len(df)} rows from CSV...")
        
        for idx, row in df.iterrows():
            name = str(row.get(name_col, '')) if name_col else ''
            
            # Skip completely empty
            if not name or name in ['nan', 'None', '']:
                empty_names += 1
                continue
            
            # LENIENT VALIDATION - only reject obvious garbage
            if not is_valid_name(name):
                rejected_count += 1
                print(f"   ❌ Rejected: {name[:50]}")
                continue
            
            # Get score
            score = 0
            if score_col:
                try:
                    score_val = float(row.get(score_col, 0))
                    score = score_val / 10 if score_val > 10 else score_val
                except:
                    score = 0
            
            # Get van number
            van = str(row.get(van_col, 'N/A')) if van_col else 'N/A'
            if van and van != 'nan' and van != 'None':
                van = van.strip()
            else:
                van = 'N/A'
            
            driver = {
                "name": name.strip(),
                "email": "N/A",
                "score": round(score, 2),
                "van_number": van,
                "trade_group": "N/A",
                "score_class": get_score_class(score)
            }
            
            drivers.append(driver)
        
        print(f"\n✅ PROCESSING SUMMARY:")
        print(f"   Total rows in CSV: {len(df)}")
        print(f"   Empty names: {empty_names}")
        print(f"   Rejected as garbage: {rejected_count}")
        print(f"   Valid drivers kept: {len(drivers)}")
        print(f"   TARGET: 213-218 drivers\n")
        
        # Sort by score (highest first)
        drivers.sort(key=lambda x: (-x['score'], x['name']))
        
        # Add ranks
        for idx, driver in enumerate(drivers):
            driver['rank'] = idx + 1
        
        # Calculate statistics
        scores = [d['score'] for d in drivers if d['score'] > 0]
        stats = {
            "total_drivers": len(drivers),
            "drivers_with_scores": len(scores),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "excellent": len([s for s in scores if s >= 9.0]),
            "good": len([s for s in scores if 8.0 <= s < 9.0]),
            "fair": len([s for s in scores if 7.0 <= s < 8.0]),
            "needs_improvement": len([s for s in scores if 6.0 <= s < 7.0]),
            "poor": len([s for s in scores if s < 6.0])
        }
        
        print(f"✅ Successfully loaded {len(drivers)} drivers (target: 213-218)")
        
        if len(drivers) < 200:
            print(f"⚠️  WARNING: Only got {len(drivers)} drivers - expected 213-218!")
            print(f"   Check the rejected names above to see what was filtered out.")
        
        return {
            "success": True,
            "statistics": stats,
            "total": len(drivers),
            "drivers": drivers,
            "source": os.path.basename(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "fleet-health-monitor"}


@app.get("/")
def root():
    return {
        "service": "Fleet Health Monitor API",
        "version": "1.0.0",
        "endpoints": {
            "drivers": "/api/drivers/excel",
            "webfleet": "/api/webfleet/engineers"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import socket
    
    def is_port_available(port):
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return True
        except OSError:
            return False
    
    # Try port 8000, fallback to 8001-8009
    port = 8000
    for p in range(8000, 8010):
        if is_port_available(p):
            port = p
            break
    
    if port != 8000:
        print(f"⚠️  Port 8000 is in use, starting on port {port} instead")
        print(f"📝 Update your frontend API URL to http://localhost:{port}")
    
    print(f"🚀 Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)