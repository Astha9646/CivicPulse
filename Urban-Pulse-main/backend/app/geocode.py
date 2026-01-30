"""Geocoding module using Google Maps Geocoding API."""
import os
import requests
from typing import Optional, Dict, Any


def geocode(text_or_address: str) -> Optional[Dict[str, float]]:
    """Geocode an address or location text to lat/lng coordinates."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("GOOGLE_MAPS_API_KEY not set, geocoding unavailable")
        return None
    
    if not text_or_address:
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": text_or_address,
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            location = data["results"][0]["geometry"]["location"]
            return {
                "lat": location["lat"],
                "lng": location["lng"]
            }
        else:
            print(f"Geocoding failed for '{text_or_address}': {data.get('status')}")
            return None
            
    except Exception as e:
        print(f"Geocoding error for '{text_or_address}': {e}")
        return None


def reverse_geocode(lat: float, lng: float) -> Optional[str]:
    """Reverse geocode coordinates to an address."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            return data["results"][0]["formatted_address"]
        else:
            return None
            
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return None
