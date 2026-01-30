"""Safety scoring module for events and routes."""
import math
from datetime import datetime
from typing import Dict, Any, List, Tuple
import polyline


def compute_score(event: Dict[str, Any]) -> float:
    """
    Compute safety score (0-100) for an event.
    Higher score = higher risk/danger.
    
    Formula:
    - severity_score = (LLM severity / 10) * 100
    - recency_decay = exp(-hours_since / 24)
    - raw_score = severity_score * recency_decay + keyword_impact
    - normalized_score = min(100, max(0, raw_score))
    """
    # Extract severity from LLM analysis (1-10 scale)
    severity = event.get("severity", 5)
    if not isinstance(severity, (int, float)) or severity < 1 or severity > 10:
        severity = 5
    
    severity_score = (severity / 10.0) * 100.0
    
    # Apply recency decay
    timestamp = event.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            timestamp = datetime.utcnow()
    elif not isinstance(timestamp, datetime):
        timestamp = datetime.utcnow()
    
    hours_since = (datetime.utcnow() - timestamp.replace(tzinfo=None)).total_seconds() / 3600.0
    decay = math.exp(-hours_since / 24.0)  # Exponential decay over 24 hours
    
    # Keyword impact (additional risk from keywords)
    keyword_impact = 0.0
    text = (event.get("title", "") + " " + event.get("text", "")).lower()
    
    # High-risk keywords
    high_risk_keywords = ["shooting", "murder", "homicide", "stabbing", "fire", "explosion"]
    if any(kw in text for kw in high_risk_keywords):
        keyword_impact += 15.0
    
    # Medium-risk keywords
    medium_risk_keywords = ["assault", "robbery", "accident", "crash", "emergency"]
    if any(kw in text for kw in medium_risk_keywords):
        keyword_impact += 8.0
    
    # Compute raw score
    raw_score = severity_score * decay + keyword_impact
    
    # Normalize to 0-100
    normalized_score = max(0.0, min(100.0, raw_score))
    
    return normalized_score


def decode_polyline(encoded_polyline: str) -> List[Tuple[float, float]]:
    """Decode Google Maps polyline to list of (lat, lng) tuples."""
    try:
        decoded = polyline.decode(encoded_polyline)
        return [(lat, lng) for lat, lng in decoded]
    except Exception as e:
        print(f"Polyline decode error: {e}")
        return []


def compute_route_risk(
    route_coordinates: List[Tuple[float, float]],
    nearby_events: List[Dict[str, Any]],
    radius_meters: float = 50.0
) -> Tuple[float, int]:
    """
    Compute aggregate risk for a route by sampling points and checking nearby events.
    
    Returns:
        (aggregate_risk_score, event_count)
    """
    if not route_coordinates:
        return 0.0, 0
    
    # Sample points along the route (every 100m or so)
    sampled_points = []
    if len(route_coordinates) <= 10:
        sampled_points = route_coordinates
    else:
        # Sample evenly along route
        step = max(1, len(route_coordinates) // 20)
        sampled_points = route_coordinates[::step]
    
    total_risk = 0.0
    event_count = 0
    
    # For each sampled point, find nearby events and aggregate risk
    for lat, lng in sampled_points:
        # Find events within radius
        nearby = []
        for event in nearby_events:
            event_coords = event.get("coordinates", {})
            event_lat = event_coords.get("lat")
            event_lng = event_coords.get("lng")
            
            if event_lat is None or event_lng is None:
                continue
            
            # Calculate distance (Haversine formula, simplified for small distances)
            distance = haversine_distance(lat, lng, event_lat, event_lng)
            
            if distance <= radius_meters:
                nearby.append((event, distance))
        
        # Weight risk by distance (closer = higher weight)
        for event, distance in nearby:
            event_risk = compute_score(event)
            # Weight decreases with distance
            weight = 1.0 - (distance / radius_meters)
            total_risk += event_risk * weight
            event_count += 1
    
    # Average risk across sampled points
    if len(sampled_points) > 0:
        aggregate_risk = total_risk / len(sampled_points)
    else:
        aggregate_risk = 0.0
    
    return aggregate_risk, event_count


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in meters using Haversine formula."""
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def normalize_route_metrics(
    routes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Normalize distance and risk metrics across routes for comparison.
    
    Returns routes with normalized_distance and normalized_risk (0-1 scale).
    """
    if not routes:
        return routes
    
    # Extract metrics
    distances = [r.get("distance_meters", 0) for r in routes]
    risks = [r.get("aggregate_risk", 0) for r in routes]
    
    # Find min/max for normalization
    min_dist = min(distances) if distances else 0
    max_dist = max(distances) if distances else 1
    min_risk = min(risks) if risks else 0
    max_risk = max(risks) if risks else 1
    
    # Normalize
    for route in routes:
        dist = route.get("distance_meters", 0)
        risk = route.get("aggregate_risk", 0)
        
        if max_dist > min_dist:
            route["normalized_distance"] = (dist - min_dist) / (max_dist - min_dist)
        else:
            route["normalized_distance"] = 0.0
        
        if max_risk > min_risk:
            route["normalized_risk"] = (risk - min_risk) / (max_risk - min_risk)
        else:
            route["normalized_risk"] = 0.0
    
    return routes
