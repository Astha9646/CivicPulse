import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { GoogleMap, LoadScript, Polyline, Marker } from '@react-google-maps/api';
import './App.css';

const API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '';

// Static libraries array to prevent LoadScript reload warnings
const LIBRARIES = ['geometry'];

const mapContainerStyle = {
  width: '100%',
  height: '100vh'
};

const defaultCenter = {
  lat: 40.7128,
  lng: -73.9857
};

const defaultZoom = 12;

function App() {
  const [events, setEvents] = useState([]);
  const [route, setRoute] = useState(null);
  const [preference, setPreference] = useState('safest');
  const [startLocation, setStartLocation] = useState('');
  const [endLocation, setEndLocation] = useState('');
  const [map, setMap] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const mapRef = useRef(null);

  const onMapLoad = useCallback((map) => {
    mapRef.current = map;
    setMap(map);
  }, []);

  // Fetch events for current map bounds
  const fetchEvents = useCallback(async () => {
    if (!map) return;

    const bounds = map.getBounds();
    if (!bounds) return;

    const ne = bounds.getNorthEast();
    const sw = bounds.getSouthWest();

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${apiUrl}/events?sw_lat=${sw.lat()}&sw_lng=${sw.lng()}&ne_lat=${ne.lat()}&ne_lng=${ne.lng()}&since_hours=24`
      );
      const data = await response.json();
      setEvents(data.events || []);
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('Failed to load safety events');
    }
  }, [map]);

  // Convert events to markers with custom styling based on safety score
  const eventMarkers = useMemo(() => {
    return events
      .filter(e => e.coordinates?.lat && e.coordinates?.lng)
      .map((e, index) => {
        const score = e.safety_score || 50;
        let color = '#48bb78'; // Green
        let size = 8;
        
        if (score >= 60) {
          color = '#f56565'; // Red
          size = 12;
        } else if (score >= 30) {
          color = '#ed8936'; // Orange
          size = 10;
        }
        
        return {
          id: e._id || index,
          position: {
            lat: e.coordinates.lat,
            lng: e.coordinates.lng
          },
          score: score,
          color: color,
          size: size,
          title: e.title || 'Safety Event'
        };
      });
  }, [events]);

  // Fetch events when map bounds change (with debounce)
  useEffect(() => {
    if (map) {
      let timeoutId;
      const listener = map.addListener('bounds_changed', () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          fetchEvents();
        }, 500); // Debounce for 500ms
      });
      return () => {
        clearTimeout(timeoutId);
        if (window.google?.maps?.event) {
          window.google.maps.event.removeListener(listener);
        }
      };
    }
  }, [map, fetchEvents]);
  
  // Create heatmap circles when map and events are ready
  useEffect(() => {
    if (!map || !window.google?.maps || eventMarkers.length === 0) return;
    
    const circles = eventMarkers.map((marker) => {
      return new window.google.maps.Circle({
        center: marker.position,
        radius: 150 + (marker.score / 100) * 100, // Radius based on score
        fillColor: marker.color,
        fillOpacity: 0.15,
        strokeColor: marker.color,
        strokeOpacity: 0.3,
        strokeWeight: 1,
        map: map
      });
    });
    
    return () => {
      circles.forEach(circle => circle.setMap(null));
    };
  }, [map, eventMarkers]);

  // Initial fetch
  useEffect(() => {
    if (map) {
      fetchEvents();
    }
  }, [map, fetchEvents]);

  // Geocode address string
  const geocodeAddress = async (address) => {
    if (!address) return null;
    
    try {
      const geocoder = new window.google.maps.Geocoder();
      return new Promise((resolve, reject) => {
        geocoder.geocode({ address }, (results, status) => {
          if (status === 'OK' && results[0]) {
            const location = results[0].geometry.location;
            resolve({
              lat: location.lat(),
              lng: location.lng()
            });
          } else {
            reject(new Error('Geocoding failed'));
          }
        });
      });
    } catch (err) {
      console.error('Geocoding error:', err);
      return null;
    }
  };

  // Calculate route
  const calculateRoute = async () => {
    if (!startLocation || !endLocation) {
      setError('Please enter both start and end locations');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const start = await geocodeAddress(startLocation);
      const end = await geocodeAddress(endLocation);

      if (!start || !end) {
        setError('Could not geocode one or both addresses');
        setLoading(false);
        return;
      }

      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          start,
          end,
          mode: 'driving',
          alpha: 0.5,
          beta: 0.5,
          preference
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Route calculation failed');
      }

      const routeData = await response.json();
      
      // Decode polyline using Google Maps geometry library
      let decodedPath = null;
      if (routeData.polyline && window.google?.maps?.geometry) {
        try {
          decodedPath = window.google.maps.geometry.encoding.decodePath(routeData.polyline);
        } catch (err) {
          console.error('Polyline decode error:', err);
        }
      }
      
      setRoute({
        ...routeData,
        decodedPath: decodedPath
      });
    } catch (err) {
      console.error('Route calculation error:', err);
      setError(err.message || 'Failed to calculate route');
    } finally {
      setLoading(false);
    }
  };

  const routeOptions = {
    strokeColor: preference === 'safest' ? '#48bb78' : '#667eea',
    strokeOpacity: 0.9,
    strokeWeight: 6,
    icons: [{
      icon: {
        path: window.google?.maps?.SymbolPath?.FORWARD_CLOSED_ARROW,
        scale: 4,
        strokeColor: preference === 'safest' ? '#48bb78' : '#667eea'
      },
      offset: '100%',
      repeat: '100px'
    }]
  };

  if (!API_KEY || API_KEY === 'your_google_maps_api_key_here') {
    return (
      <div className="error-container">
        <h1>Google Maps API Key Required</h1>
        <p>Please set REACT_APP_GOOGLE_MAPS_API_KEY in your .env file.</p>
        <p style={{ marginTop: '20px', fontSize: '14px', opacity: 0.8 }}>
          Current value: {API_KEY ? 'Set but may be invalid' : 'Not set'}
        </p>
        <p style={{ marginTop: '10px', fontSize: '12px', opacity: 0.6 }}>
          Make sure your API key has the following APIs enabled:<br/>
          - Maps JavaScript API<br/>
          - Geocoding API<br/>
          - Directions API
        </p>
      </div>
    );
  }

  const getSafetyColor = (score) => {
    if (score < 30) return '#48bb78'; // Green
    if (score < 60) return '#ed8936'; // Orange
    return '#f56565'; // Red
  };

  const getSafetyLabel = (score) => {
    if (score < 30) return 'Safe';
    if (score < 60) return 'Moderate';
    return 'High Risk';
  };

  return (
    <LoadScript
      googleMapsApiKey={API_KEY}
      libraries={LIBRARIES}
      loadingElement={<div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0a0e27', color: 'white' }}>Loading Maps...</div>}
      onError={(error) => {
        console.error('Google Maps LoadScript error:', error);
        setError('Failed to load Google Maps. Please check your API key.');
      }}
    >
      <div className="app-container">
        <div className="control-panel">
          <h1>Urban Pulse</h1>
          <p style={{ 
            color: '#718096', 
            fontSize: '14px', 
            marginBottom: '24px',
            fontWeight: 500
          }}>
            Real-time safety intelligence for smarter navigation
          </p>
          <div className="controls">
            <div className="input-group">
              <label>📍 Start Location</label>
              <input
                type="text"
                value={startLocation}
                onChange={(e) => setStartLocation(e.target.value)}
                placeholder="e.g., Times Square, NYC"
                onKeyPress={(e) => e.key === 'Enter' && calculateRoute()}
              />
            </div>
            <div className="input-group">
              <label>🎯 End Location</label>
              <input
                type="text"
                value={endLocation}
                onChange={(e) => setEndLocation(e.target.value)}
                placeholder="e.g., Central Park, NYC"
                onKeyPress={(e) => e.key === 'Enter' && calculateRoute()}
              />
            </div>
            <div className="input-group">
              <label>⚙️ Route Preference</label>
              <select
                value={preference}
                onChange={(e) => setPreference(e.target.value)}
              >
                <option value="fastest">⚡ Fastest Route</option>
                <option value="safest">🛡️ Safest Route</option>
              </select>
            </div>
            <button
              onClick={calculateRoute}
              disabled={loading}
              className="route-button"
            >
              {loading ? '⏳ Calculating...' : '🚀 Calculate Route'}
            </button>
            {route && (
              <div className="route-info">
                <h3>Route Details</h3>
                <p>
                  <strong>Distance:</strong>
                  <span style={{ color: '#667eea', fontWeight: 700 }}>
                    {(route.distance_meters / 1000).toFixed(2)} km
                  </span>
                </p>
                <p>
                  <strong>Duration:</strong>
                  <span style={{ color: '#667eea', fontWeight: 700 }}>
                    {Math.round(route.duration_seconds / 60)} min
                  </span>
                </p>
                <p>
                  <strong>Safety Level:</strong>
                  <span style={{ 
                    color: getSafetyColor(route.aggregate_risk), 
                    fontWeight: 700,
                    padding: '4px 12px',
                    borderRadius: '8px',
                    background: `${getSafetyColor(route.aggregate_risk)}20`,
                    fontSize: '13px'
                  }}>
                    {getSafetyLabel(route.aggregate_risk)}
                  </span>
                </p>
                <p>
                  <strong>Risk Score:</strong>
                  <span style={{ 
                    color: getSafetyColor(route.aggregate_risk),
                    fontWeight: 700 
                  }}>
                    {route.aggregate_risk.toFixed(1)}/100
                  </span>
                </p>
                <p>
                  <strong>Nearby Events:</strong>
                  <span style={{ color: '#667eea', fontWeight: 700 }}>
                    {route.event_count}
                  </span>
                </p>
              </div>
            )}
            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}
            {events.length > 0 && (
              <div style={{
                marginTop: '16px',
                padding: '12px',
                background: 'linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%)',
                borderRadius: '12px',
                fontSize: '13px',
                color: '#234e52',
                fontWeight: 500,
                textAlign: 'center'
              }}>
                📍 {events.length} safety events detected in this area
              </div>
            )}
          </div>
        </div>
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={defaultCenter}
          zoom={defaultZoom}
          onLoad={onMapLoad}
          options={{
            mapTypeControl: true,
            streetViewControl: true,
            fullscreenControl: true,
            styles: [
              {
                featureType: 'all',
                elementType: 'geometry',
                stylers: [{ color: '#242f3e' }]
              },
              {
                featureType: 'all',
                elementType: 'labels.text.stroke',
                stylers: [{ color: '#242f3e' }]
              },
              {
                featureType: 'all',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#746855' }]
              },
              {
                featureType: 'water',
                elementType: 'geometry',
                stylers: [{ color: '#17263c' }]
              },
              {
                featureType: 'road',
                elementType: 'geometry',
                stylers: [{ color: '#38414e' }]
              },
              {
                featureType: 'road',
                elementType: 'geometry.stroke',
                stylers: [{ color: '#212a37' }]
              },
              {
                featureType: 'road',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#9ca5b3' }]
              },
              {
                featureType: 'poi',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#d59563' }]
              }
            ]
          }}
        >
          {/* Custom markers for safety events (replacing deprecated HeatmapLayer) */}
          {eventMarkers.map((marker) => (
            <Marker
              key={marker.id}
              position={marker.position}
              title={`${marker.title} - Risk Score: ${marker.score.toFixed(1)}`}
              icon={{
                path: window.google?.maps?.SymbolPath?.CIRCLE,
                scale: marker.size,
                fillColor: marker.color,
                fillOpacity: 0.8,
                strokeColor: '#ffffff',
                strokeWeight: 2
              }}
            />
          ))}
          {route?.decodedPath && route.decodedPath.length > 0 && (
            <Polyline
              path={route.decodedPath}
              options={routeOptions}
            />
          )}
        </GoogleMap>
      </div>
    </LoadScript>
  );
}

export default App;
