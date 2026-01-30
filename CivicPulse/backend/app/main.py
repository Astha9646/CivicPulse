"""FastAPI main application."""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .db import db
from .scraper import run_one_shot
from .llm import analyze_signal
from .geocode import geocode
from .scoring import compute_score, compute_route_risk, decode_polyline, normalize_route_metrics
import requests


app = FastAPI(title="Urban Pulse API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class IngestResponse(BaseModel):
    message: str
    events_processed: int
    events_stored: int


class EventResponse(BaseModel):
    _id: str
    source: str
    title: str
    text: str
    timestamp: str
    coordinates: Dict[str, float]
    safety_score: float
    event_type: str
    severity: int


class RouteRequest(BaseModel):
    start: Dict[str, float] = Field(..., description="Start location with lat and lng")
    end: Dict[str, float] = Field(..., description="End location with lat and lng")
    mode: str = Field(default="driving", description="Transportation mode: driving, walking, bicycling, transit")
    alpha: float = Field(default=0.5, description="Weight for distance in route selection")
    beta: float = Field(default=0.5, description="Weight for risk in route selection")
    preference: str = Field(default="safest", description="Route preference: fastest or safest")


class RouteResponse(BaseModel):
    route: Dict[str, Any]
    distance_meters: float
    duration_seconds: float
    aggregate_risk: float
    event_count: int
    preference: str
    polyline: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    try:
        await db.connect()
    except Exception as e:
        print(f"Warning: Database connection failed: {e}")
        print("App will continue but database operations may fail")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await db.disconnect()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/ingest/one-shot", response_model=IngestResponse)
async def ingest_one_shot():
    """Run a one-shot data ingestion from all configured sources."""
    try:
        articles = run_one_shot()
        events_stored = 0
        
        for article in articles:
            try:
                # Analyze with LLM
                analysis = analyze_signal(article["text"])
                
                # Geocode if address hint exists
                coordinates = None
                if analysis.get("address_hint"):
                    coordinates = geocode(analysis["address_hint"])
                
                # If geocoding failed, try geocoding the title or first part of text
                if not coordinates:
                    # Try to geocode title or first sentence
                    geocode_text = article.get("title", "")[:100]
                    coordinates = geocode(geocode_text)
                
                # Skip if no coordinates found
                if not coordinates:
                    print(f"Skipping article (no coordinates): {article.get('title', 'No title')}")
                    continue
                
                # Create event document
                event = {
                    "source": article["source"],
                    "title": article.get("title", ""),
                    "text": article.get("text", ""),
                    "url": article.get("url", ""),
                    "timestamp": article.get("published", datetime.utcnow()),
                    "coordinates": {
                        "type": "Point",
                        "coordinates": [coordinates["lng"], coordinates["lat"]],
                        "lat": coordinates["lat"],
                        "lng": coordinates["lng"]
                    },
                    "event_type": analysis.get("type", "other"),
                    "severity": analysis.get("severity", 5),
                    "urgency": analysis.get("urgency", 0),
                    "address_hint": analysis.get("address_hint"),
                    "notes": analysis.get("notes", "")
                }
                
                # Compute safety score
                event["safety_score"] = compute_score(event)
                
                # Store in database
                await db.insert_event(event)
                events_stored += 1
                
            except Exception as e:
                print(f"Error processing article: {e}")
                continue
        
        return IngestResponse(
            message="Ingestion completed",
            events_processed=len(articles),
            events_stored=events_stored
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/events")
async def get_events(
    sw_lat: Optional[float] = None,
    sw_lng: Optional[float] = None,
    ne_lat: Optional[float] = None,
    ne_lng: Optional[float] = None,
    since_hours: Optional[int] = 24
):
    """Get safety events within bounding box and time window."""
    try:
        bbox = None
        if all(x is not None for x in [sw_lat, sw_lng, ne_lat, ne_lng]):
            bbox = {
                "sw": {"lat": sw_lat, "lng": sw_lng},
                "ne": {"lat": ne_lat, "lng": ne_lng}
            }
        
        events = await db.query_events(bbox=bbox, since_hours=since_hours)
        
        # Format for frontend
        formatted_events = []
        for event in events:
            coords = event.get("coordinates", {})
            formatted_events.append({
                "_id": event.get("_id"),
                "source": event.get("source", ""),
                "title": event.get("title", ""),
                "text": event.get("text", "")[:200],  # Truncate for response
                "timestamp": event.get("timestamp"),
                "coordinates": {
                    "lat": coords.get("lat") if isinstance(coords, dict) else None,
                    "lng": coords.get("lng") if isinstance(coords, dict) else None
                },
                "safety_score": event.get("safety_score", 0),
                "event_type": event.get("event_type", "other"),
                "severity": event.get("severity", 5)
            })
        
        return {"events": formatted_events, "count": len(formatted_events)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/route", response_model=RouteResponse)
async def get_route(request: RouteRequest):
    """Get route with safety analysis."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_MAPS_API_KEY not configured")
    
    try:
        start = request.start
        end = request.end
        mode = request.mode
        preference = request.preference
        alpha = request.alpha
        beta = request.beta
        
        # Normalize weights
        total_weight = alpha + beta
        if total_weight > 0:
            alpha = alpha / total_weight
            beta = beta / total_weight
        else:
            alpha = 0.5
            beta = 0.5
        
        # Call Google Directions API
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": f"{start['lat']},{start['lng']}",
            "destination": f"{end['lat']},{end['lng']}",
            "mode": mode,
            "alternatives": "true",  # Get alternative routes
            "key": api_key
        }
        
        response = requests.get(directions_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") != "OK" or not data.get("routes"):
            raise HTTPException(status_code=400, detail=f"Directions API error: {data.get('status')}")
        
        routes_data = data["routes"]
        
        # Process each route
        processed_routes = []
        
        for route in routes_data:
            leg = route["legs"][0]
            distance_meters = leg["distance"]["value"]
            duration_seconds = leg["duration"]["value"]
            
            # Decode polyline
            encoded_polyline = route["overview_polyline"]["points"]
            route_coordinates = decode_polyline(encoded_polyline)
            
            # Find nearby events along route
            all_nearby_events = []
            for lat, lng in route_coordinates[::max(1, len(route_coordinates)//20)]:  # Sample points
                nearby = await db.find_nearby_events(lat, lng, radius_meters=50)
                all_nearby_events.extend(nearby)
            
            # Remove duplicates
            seen_ids = set()
            unique_events = []
            for event in all_nearby_events:
                event_id = event.get("_id")
                if event_id and event_id not in seen_ids:
                    seen_ids.add(event_id)
                    unique_events.append(event)
            
            # Compute aggregate risk
            aggregate_risk, event_count = compute_route_risk(
                route_coordinates,
                unique_events,
                radius_meters=50.0
            )
            
            processed_routes.append({
                "route": route,
                "distance_meters": distance_meters,
                "duration_seconds": duration_seconds,
                "aggregate_risk": aggregate_risk,
                "event_count": event_count,
                "polyline": encoded_polyline,
                "coordinates": route_coordinates
            })
        
        # Normalize metrics
        processed_routes = normalize_route_metrics(processed_routes)
        
        # Select route based on preference
        if preference == "fastest":
            # Choose route with shortest duration
            selected_route = min(processed_routes, key=lambda r: r["duration_seconds"])
        else:  # safest
            # Choose route minimizing alpha*norm_distance + beta*norm_risk
            selected_route = min(
                processed_routes,
                key=lambda r: alpha * r.get("normalized_distance", 0) + beta * r.get("normalized_risk", 0)
            )
        
        return RouteResponse(
            route=selected_route["route"],
            distance_meters=selected_route["distance_meters"],
            duration_seconds=selected_route["duration_seconds"],
            aggregate_risk=selected_route["aggregate_risk"],
            event_count=selected_route["event_count"],
            preference=preference,
            polyline=selected_route["polyline"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route calculation failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
