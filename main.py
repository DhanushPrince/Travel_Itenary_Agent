import os
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from mcp_itinerary_scraper import ItineraryRequest, process_itinerary_request
import uuid
import json
from pathlib import Path

# Create necessary directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("cache", exist_ok=True)

app = FastAPI(title="Travel Itinerary Generator")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store ongoing and completed itineraries
itinerary_tasks = {}
itinerary_results = {}

class ItineraryRequestData(BaseModel):
    location: str
    category: str
    days: int = 3
    interests: Optional[List[str]] = None
    budget: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-itinerary")
async def generate_itinerary(request_data: ItineraryRequestData, background_tasks: BackgroundTasks):
    """Endpoint to initiate itinerary generation."""
    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())
    
    # Convert to our internal model
    itinerary_request = ItineraryRequest(
        location=request_data.location,
        category=request_data.category,
        days=request_data.days,
        interests=request_data.interests if request_data.interests else None,
        budget=request_data.budget if request_data.budget else None
    )
    
    # Check if we have a cached result for similar request
    cache_file = Path(f"cache/{request_data.location}_{request_data.category}_{request_data.days}.json")
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
                if cached_data.get("interests") == request_data.interests and cached_data.get("budget") == request_data.budget:
                    return {"request_id": request_id, "status": "completed", "itinerary": cached_data.get("itinerary")}
        except Exception:
            # If any error occurs with cache, just proceed with normal generation
            pass
    
    # Start processing in the background
    background_tasks.add_task(process_itinerary_in_background, request_id, itinerary_request)
    
    # Return the request ID so the client can poll for results
    return {"request_id": request_id, "status": "processing"}

async def process_itinerary_in_background(request_id: str, itinerary_request: ItineraryRequest):
    """Background task to process the itinerary request."""
    try:
        # Process the request
        itinerary = await process_itinerary_request(itinerary_request)
        
        # Store the result
        itinerary_results[request_id] = {
            "status": "completed",
            "itinerary": itinerary
        }
        
        # Cache the result
        try:
            cache_data = {
                "location": itinerary_request.location,
                "category": itinerary_request.category,
                "days": itinerary_request.days,
                "interests": itinerary_request.interests,
                "budget": itinerary_request.budget,
                "itinerary": itinerary
            }
            cache_file = f"cache/{itinerary_request.location}_{itinerary_request.category}_{itinerary_request.days}.json"
            with open(cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Error caching result: {e}")
            
    except Exception as e:
        itinerary_results[request_id] = {
            "status": "error",
            "message": str(e)
        }

@app.get("/itinerary-status/{request_id}")
async def get_itinerary_status(request_id: str):
    """Check the status of an itinerary generation request."""
    # Check if the result is ready
    if request_id in itinerary_results:
        return itinerary_results[request_id]
    
    # If not found in results, it's still processing or invalid
    return {"status": "processing" if request_id in itinerary_tasks else "not_found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)