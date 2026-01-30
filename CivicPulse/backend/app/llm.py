"""LLM analysis module for classifying safety events."""
import os
import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI


EVENT_TYPES = [
    "major_crime",
    "minor_crime",
    "accident",
    "environmental",
    "infrastructure",
    "public_disorder",
    "other"
]


def analyze_signal_fallback(text: str) -> Dict[str, Any]:
    """Fallback analysis using regex patterns when LLM is unavailable."""
    text_lower = text.lower()
    
    # Determine event type
    event_type = "other"
    severity = 5  # Default medium severity
    
    # Major crime keywords
    major_crime_keywords = ["murder", "homicide", "shooting", "stabbing", "rape", "assault with weapon", "armed robbery"]
    if any(kw in text_lower for kw in major_crime_keywords):
        event_type = "major_crime"
        severity = 9
    
    # Minor crime keywords
    elif any(kw in text_lower for kw in ["theft", "burglary", "vandalism", "petty theft", "shoplifting"]):
        event_type = "minor_crime"
        severity = 4
    
    # Accident keywords
    elif any(kw in text_lower for kw in ["accident", "crash", "collision", "car accident", "traffic accident"]):
        event_type = "accident"
        severity = 6
    
    # Environmental keywords
    elif any(kw in text_lower for kw in ["fire", "flood", "storm", "natural disaster", "hazardous material"]):
        event_type = "environmental"
        severity = 7
    
    # Infrastructure keywords
    elif any(kw in text_lower for kw in ["power outage", "water main", "bridge", "road closure", "construction"]):
        event_type = "infrastructure"
        severity = 5
    
    # Public disorder keywords
    elif any(kw in text_lower for kw in ["protest", "riot", "disturbance", "unrest", "crowd"]):
        event_type = "public_disorder"
        severity = 6
    
    # Extract address hints using common patterns
    address_hint = None
    address_patterns = [
        r'\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl)',
        r'[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)',
        r'\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd)',
    ]
    
    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            address_hint = match.group(0)
            break
    
    # If no address found, try to extract neighborhood/area names
    if not address_hint:
        neighborhood_patterns = [
            r'(?:in|at|near|on)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:neighborhood|area|district|borough)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:neighborhood|area|district)'
        ]
        for pattern in neighborhood_patterns:
            match = re.search(pattern, text)
            if match:
                address_hint = match.group(1)
                break
    
    return {
        "type": event_type,
        "severity": severity,
        "address_hint": address_hint,
        "notes": "Fallback regex analysis",
        "urgency": severity * 10 - 50  # Convert 1-10 to -50 to 50 range
    }


def analyze_signal(text: str) -> Dict[str, Any]:
    """Analyze a safety signal using OpenAI LLM or fallback."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("OPENAI_API_KEY not set, using fallback analysis")
        return analyze_signal_fallback(text)
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""Analyze the following news article or social media post about a safety-related event. Extract key information and classify it.

Text:
{text[:2000]}  # Limit text length

Please provide a JSON response with the following structure:
{{
    "type": one of ["major_crime", "minor_crime", "accident", "environmental", "infrastructure", "public_disorder", "other"],
    "severity": integer from 1-10 (1=very minor, 10=very severe),
    "address_hint": any address, street name, neighborhood, or location mentioned in the text (or null if none),
    "notes": brief summary of the event,
    "urgency": integer from -100 to 100 representing urgency/impact (-100=very safe/positive, 0=neutral, 100=very urgent/dangerous)
}}

Focus on:
- Classifying the event type accurately
- Assessing severity based on potential harm to public safety
- Extracting any location information (addresses, street names, neighborhoods, landmarks)
- Determining urgency based on recency, severity, and potential impact

Return ONLY valid JSON, no additional text."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a safety analysis expert. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        result = json.loads(response_text)
        
        # Validate and normalize result
        if result.get("type") not in EVENT_TYPES:
            result["type"] = "other"
        
        severity = result.get("severity", 5)
        if not isinstance(severity, int) or severity < 1 or severity > 10:
            severity = 5
        result["severity"] = severity
        
        urgency = result.get("urgency", severity * 10 - 50)
        if not isinstance(urgency, int):
            urgency = severity * 10 - 50
        if urgency < -100:
            urgency = -100
        if urgency > 100:
            urgency = 100
        result["urgency"] = urgency
        
        return result
        
    except Exception as e:
        print(f"OpenAI API error: {e}, using fallback")
        return analyze_signal_fallback(text)
