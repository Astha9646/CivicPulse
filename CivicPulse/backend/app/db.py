"""MongoDB database connection and operations."""
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure


class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.collection = None

    async def connect(self):
        """Connect to MongoDB."""
        mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/urbanpulse")
        try:
            self.client = AsyncIOMotorClient(mongo_uri)
            # Test connection
            await self.client.admin.command('ping')
            db_name = mongo_uri.split('/')[-1] if '/' in mongo_uri else "urbanpulse"
            self.db = self.client[db_name]
            self.collection = self.db.events
            # Create indexes
            # Note: 2dsphere index requires GeoJSON format: {type: "Point", coordinates: [lng, lat]}
            try:
                await self.collection.create_index([("coordinates", "2dsphere")])
            except Exception as e:
                print(f"Warning: Could not create 2dsphere index: {e}")
            await self.collection.create_index([("timestamp", -1)])
            await self.collection.create_index([("source", 1)])
            print(f"Connected to MongoDB: {db_name}")
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()

    async def insert_event(self, event: Dict[str, Any]) -> str:
        """Insert a safety event into the database."""
        if self.collection is None:
            await self.connect()
        
        event["created_at"] = datetime.utcnow()
        result = await self.collection.insert_one(event)
        return str(result.inserted_id)

    async def query_events(
        self,
        bbox: Optional[Dict[str, float]] = None,
        since_hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query events within bounding box and time window."""
        if self.collection is None:
            await self.connect()
        
        query = {}
        
        # Time filter
        if since_hours:
            since_time = datetime.utcnow() - timedelta(hours=since_hours)
            query["timestamp"] = {"$gte": since_time}
        
        # Geographic filter - use GeoJSON format for 2dsphere index
        if bbox:
            query["coordinates"] = {
                "$geoWithin": {
                    "$geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [bbox["sw"]["lng"], bbox["sw"]["lat"]],
                            [bbox["ne"]["lng"], bbox["sw"]["lat"]],
                            [bbox["ne"]["lng"], bbox["ne"]["lat"]],
                            [bbox["sw"]["lng"], bbox["ne"]["lat"]],
                            [bbox["sw"]["lng"], bbox["sw"]["lat"]]
                        ]]
                    }
                }
            }
        
        cursor = self.collection.find(query)
        events = await cursor.to_list(length=10000)  # Limit for safety
        
        # Convert ObjectId to string
        for event in events:
            event["_id"] = str(event["_id"])
            if isinstance(event.get("timestamp"), datetime):
                event["timestamp"] = event["timestamp"].isoformat()
            if isinstance(event.get("created_at"), datetime):
                event["created_at"] = event["created_at"].isoformat()
        
        return events

    async def find_nearby_events(
        self,
        lat: float,
        lng: float,
        radius_meters: float = 50
    ) -> List[Dict[str, Any]]:
        """Find events within radius of a point."""
        if self.collection is None:
            await self.connect()
        
        query = {
            "coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "$maxDistance": radius_meters
                }
            }
        }
        
        cursor = self.collection.find(query)
        events = await cursor.to_list(length=1000)
        
        for event in events:
            event["_id"] = str(event["_id"])
            if isinstance(event.get("timestamp"), datetime):
                event["timestamp"] = event["timestamp"].isoformat()
        
        return events


# Global database instance
db = Database()
