"""Demo seed script to insert sample safety events."""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.db import db


# Sample demo events (NYC area)
DEMO_EVENTS = [
    {
        "source": "demo:seed",
        "title": "Traffic Accident on Broadway",
        "text": "Multi-vehicle accident reported on Broadway near Times Square. Emergency services on scene.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=2),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9857, 40.7580],
            "lat": 40.7580,
            "lng": -73.9857
        },
        "event_type": "accident",
        "severity": 6,
        "urgency": 40,
        "address_hint": "Broadway, Times Square",
        "notes": "Demo event: traffic accident",
        "safety_score": 45.0
    },
    {
        "source": "demo:seed",
        "title": "Theft Reported in Central Park",
        "text": "Petty theft incident reported near Central Park entrance. Police investigating.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=5),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9654, 40.7829],
            "lat": 40.7829,
            "lng": -73.9654
        },
        "event_type": "minor_crime",
        "severity": 4,
        "urgency": 20,
        "address_hint": "Central Park",
        "notes": "Demo event: minor crime",
        "safety_score": 25.0
    },
    {
        "source": "demo:seed",
        "title": "Fire Alarm in Financial District",
        "text": "Fire alarm activated in office building. Fire department responding.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=1),
        "coordinates": {
            "type": "Point",
            "coordinates": [-74.0060, 40.7128],
            "lat": 40.7128,
            "lng": -74.0060
        },
        "event_type": "environmental",
        "severity": 7,
        "urgency": 60,
        "address_hint": "Financial District",
        "notes": "Demo event: fire alarm",
        "safety_score": 65.0
    },
    {
        "source": "demo:seed",
        "title": "Road Closure on Brooklyn Bridge",
        "text": "Scheduled maintenance causing road closure on Brooklyn Bridge. Use alternate route.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=12),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9969, 40.7061],
            "lat": 40.7061,
            "lng": -73.9969
        },
        "event_type": "infrastructure",
        "severity": 5,
        "urgency": 30,
        "address_hint": "Brooklyn Bridge",
        "notes": "Demo event: infrastructure",
        "safety_score": 20.0
    },
    {
        "source": "demo:seed",
        "title": "Assault Reported in Queens",
        "text": "Assault incident reported. Police investigation ongoing.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=8),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9442, 40.7282],
            "lat": 40.7282,
            "lng": -73.9442
        },
        "event_type": "major_crime",
        "severity": 8,
        "urgency": 70,
        "address_hint": "Queens",
        "notes": "Demo event: major crime",
        "safety_score": 50.0
    },
    {
        "source": "demo:seed",
        "title": "Car Crash on FDR Drive",
        "text": "Two-car collision on FDR Drive causing traffic delays.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=3),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9712, 40.7505],
            "lat": 40.7505,
            "lng": -73.9712
        },
        "event_type": "accident",
        "severity": 5,
        "urgency": 35,
        "address_hint": "FDR Drive",
        "notes": "Demo event: car crash",
        "safety_score": 30.0
    },
    {
        "source": "demo:seed",
        "title": "Vandalism in Lower East Side",
        "text": "Property damage reported. Minor vandalism incident.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=15),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9903, 40.7181],
            "lat": 40.7181,
            "lng": -73.9903
        },
        "event_type": "minor_crime",
        "severity": 3,
        "urgency": 10,
        "address_hint": "Lower East Side",
        "notes": "Demo event: vandalism",
        "safety_score": 10.0
    },
    {
        "source": "demo:seed",
        "title": "Power Outage in Upper West Side",
        "text": "Temporary power outage affecting several blocks. Utility company working on restoration.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=6),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9772, 40.7851],
            "lat": 40.7851,
            "lng": -73.9772
        },
        "event_type": "infrastructure",
        "severity": 6,
        "urgency": 40,
        "address_hint": "Upper West Side",
        "notes": "Demo event: power outage",
        "safety_score": 35.0
    },
    {
        "source": "demo:seed",
        "title": "Protest Activity in Midtown",
        "text": "Peaceful protest gathering reported. Increased police presence.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=4),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9851, 40.7549],
            "lat": 40.7549,
            "lng": -73.9851
        },
        "event_type": "public_disorder",
        "severity": 4,
        "urgency": 25,
        "address_hint": "Midtown",
        "notes": "Demo event: protest",
        "safety_score": 20.0
    },
    {
        "source": "demo:seed",
        "title": "Burglary Attempt in Harlem",
        "text": "Attempted burglary reported. Suspect fled scene. Police investigating.",
        "url": "",
        "timestamp": datetime.utcnow() - timedelta(hours=10),
        "coordinates": {
            "type": "Point",
            "coordinates": [-73.9442, 40.8075],
            "lat": 40.8075,
            "lng": -73.9442
        },
        "event_type": "minor_crime",
        "severity": 5,
        "urgency": 30,
        "address_hint": "Harlem",
        "notes": "Demo event: burglary",
        "safety_score": 25.0
    }
]


async def seed_demo():
    """Seed database with demo events."""
    try:
        await db.connect()
        
        print("Seeding demo events...")
        count = 0
        
        for event in DEMO_EVENTS:
            try:
                await db.insert_event(event)
                count += 1
                print(f"Inserted: {event['title']}")
            except Exception as e:
                print(f"Error inserting {event['title']}: {e}")
        
        print(f"\nSuccessfully seeded {count} demo events")
        await db.disconnect()
        
    except Exception as e:
        print(f"Seed failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_demo())
