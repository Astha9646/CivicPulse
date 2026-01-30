<div align="center">

# 🌆 Urban Pulse

### AI-Powered Safety Routing & Real-Time Risk Assessment System

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/vijayshreepathak/Urban-Pulse)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/vijayshreevaibhav/)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-FF6B6B?style=for-the-badge&logo=google-chrome)](https://vijayshreepathak.netlify.app/)

**Urban Pulse** is an intelligent safety overlay system that aggregates real-time safety signals from multiple sources, analyzes them using advanced LLM technology, and provides smart route recommendations based on comprehensive risk assessment.

*Built for hackathons • Designed for real-world impact*

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🔄 System Flow](#-system-flow)
- [🚀 Quick Start](#-quick-start)
- [📡 API Reference](#-api-reference)
- [🧮 Safety Scoring Algorithm](#-safety-scoring-algorithm)
- [💻 Technology Stack](#-technology-stack)
- [🛠️ Development](#️-development)
- [📊 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [❓ Troubleshooting](#-troubleshooting)
- [🎯 Use Cases](#-use-cases)
- [⚠️ Disclaimer](#️-disclaimer)
- [👩‍💻 Author](#-author)
- [📄 License](#-license)

---

## ✨ Features

### 🎯 Core Capabilities

- **🔍 Multi-Source Data Aggregation**
  - RSS feeds from city news and police departments
  - Reddit community posts from city subreddits
  - HTML scraping of police blotters
  - Real-time data ingestion pipeline

- **🤖 AI-Powered Analysis**
  - OpenAI GPT-3.5-turbo for intelligent event classification
  - Automatic event type detection (crime, accident, environmental, etc.)
  - Severity assessment (1-10 scale)
  - Urgency scoring (-100 to +100)
  - Location extraction from unstructured text
  - Regex-based fallback when API unavailable

- **📊 Advanced Safety Scoring**
  - Exponential recency decay (24-hour half-life)
  - Keyword-based impact analysis
  - Normalization to 0-100 risk scale
  - Real-time score computation

- **🗺️ Smart Routing**
  - Integration with Google Directions API
  - Alternative route analysis
  - Aggregate risk computation along routes
  - Customizable distance vs. safety tradeoffs
  - "Fastest" vs. "Safest" route selection

- **🎨 Modern Visualization**
  - Interactive Google Maps integration
  - Custom heatmap-style event markers
  - Color-coded safety indicators
  - Real-time route rendering
  - Glassmorphic UI design
  - Dark theme optimized

- **🔒 Production-Ready Architecture**
  - Dockerized microservices
  - MongoDB with geospatial indexing
  - FastAPI async backend
  - React frontend with hot-reload
  - CORS-enabled API
  - Comprehensive error handling

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          URBAN PULSE SYSTEM                              │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES LAYER                                │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐               │
│  │  RSS Feeds   │  │   Reddit     │  │ Police Blotters │               │
│  │  (City News) │  │ (Subreddits) │  │  (HTML Scrape)  │               │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘               │
│         │                  │                    │                        │
│         └──────────────────┴────────────────────┘                        │
│                            │                                             │
└────────────────────────────┼─────────────────────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                       BACKEND SERVICE LAYER                               │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Application                           │    │
│  │                    (Python 3.11 + Uvicorn)                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   Scraper    │  │  LLM Engine  │  │   Geocoder   │  │  Scoring  │  │
│  │   Module     │→ │  (OpenAI)    │→ │  (G-Maps)    │→ │  Engine   │  │
│  │              │  │              │  │              │  │           │  │
│  │ • feedparser │  │ • GPT-3.5    │  │ • Geocoding  │  │ • Decay   │  │
│  │ • BeautifulS │  │ • JSON parse │  │ • Address    │  │ • Keywords│  │
│  │ • RSS/HTML   │  │ • Fallback   │  │   resolution │  │ • Normali │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    API Endpoints                                 │    │
│  │  • POST /ingest/one-shot  - Data ingestion                       │    │
│  │  • GET  /events           - Query safety events                  │    │
│  │  • POST /route            - Calculate safe routes                │    │
│  │  • GET  /health           - Health check                         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     MongoDB 7.0                                  │    │
│  │                                                                  │    │
│  │  • Geospatial 2dsphere indexing                                 │    │
│  │  • Event storage with coordinates                               │    │
│  │  • Timestamp-based queries                                      │    │
│  │  • Bounding box queries                                         │    │
│  │  • $near and $geoWithin operations                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    React Application                             │    │
│  │                 (@react-google-maps/api)                         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   Google     │  │   Heatmap    │  │    Route     │  │   Modern  │  │
│  │   Maps UI    │  │   Markers    │  │  Visualizer  │  │    UI     │  │
│  │              │  │              │  │              │  │           │  │
│  │ • Interactive│  │ • Color-     │  │ • Polylines  │  │ • Glass-  │  │
│  │ • Custom     │  │   coded      │  │ • Safety     │  │   morphic │  │
│  │   dark theme │  │ • Size-based │  │   metrics    │  │ • Controls│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘  │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   OpenAI     │  │    Google    │  │    Google    │                  │
│  │     API      │  │  Geocoding   │  │  Directions  │                  │
│  │              │  │     API      │  │     API      │                  │
│  │ • GPT-3.5    │  │ • Address to │  │ • Route      │                  │
│  │ • Analysis   │  │   lat/lng    │  │   planning   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction

```
User Request → Frontend (React)
                  ↓
          API Call (fetch)
                  ↓
          Backend (FastAPI)
                  ↓
       ┌──────────┴──────────┐
       ↓                     ↓
   Database            External APIs
   (MongoDB)          (OpenAI, Google)
       ↓                     ↓
   Query Results      API Responses
       ↓                     ↓
       └──────────┬──────────┘
                  ↓
          Process & Score
                  ↓
          JSON Response
                  ↓
          Frontend Update
                  ↓
          User Sees Results
```

---

## 🔄 System Flow

### Data Ingestion Pipeline

```
1. SCRAPING
   RSS Feeds → Parse entries → Extract text + timestamp
   Reddit → Fetch RSS → Parse posts
   Police Blotters → HTML scrape → Extract incidents

2. LLM ANALYSIS
   Raw text → OpenAI GPT-3.5-turbo → Structured output
   ├─ Event type classification
   ├─ Severity (1-10)
   ├─ Address hint extraction
   ├─ Urgency score (-100 to 100)
   └─ Summary notes

3. GEOCODING
   Address hint → Google Geocoding API → Lat/Lng coordinates
   (Skip event if geocoding fails)

4. SCORING
   Event + Timestamp → Safety Score Engine → 0-100 risk score
   ├─ Severity contribution
   ├─ Recency decay (exp function)
   ├─ Keyword impact
   └─ Normalization

5. STORAGE
   Event object → MongoDB → Geospatial indexed collection
```

### Route Calculation Flow

```
1. USER INPUT
   Start location + End location + Preference (fastest/safest)

2. DIRECTIONS API
   Query Google Directions → Get multiple route alternatives

3. ROUTE ANALYSIS
   For each route:
   ├─ Decode polyline
   ├─ Sample points along route
   ├─ Query nearby events (50m radius)
   ├─ Compute aggregate risk
   └─ Count events

4. NORMALIZATION
   Normalize distance and risk across all routes → 0-1 scale

5. SELECTION
   If "fastest": Choose minimum duration
   If "safest": Choose minimum (α × distance + β × risk)

6. RESPONSE
   Return selected route with metrics + polyline
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Google Maps API Key** with the following APIs enabled:
  - Maps JavaScript API
  - Geocoding API
  - Directions API
- **OpenAI API Key** (optional, fallback mode available)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/vijayshreepathak/Urban-Pulse.git
cd Urban-Pulse
```

2. **Set up environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_MAPS_API_KEY=AIza-your-google-maps-key-here
MONGO_URI=mongodb://mongo:27017/urbanpulse
```

3. **Build and start all services**

```bash
docker-compose up --build
```

This will start:
- MongoDB on `localhost:27017`
- Backend API on `localhost:8000`
- Frontend UI on `localhost:3000`

4. **Seed demo data** (optional but recommended)

```bash
docker-compose exec backend python -m app.scripts.seed_demo
```

5. **Access the application**

- 🌐 Frontend: **http://localhost:3000**
- 🔌 Backend API: **http://localhost:8000**
- 📚 API Documentation: **http://localhost:8000/docs**

---

## 📡 API Reference

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-18T12:00:00"
}
```

---

### Ingest Safety Signals

```http
POST /ingest/one-shot
```

Runs a one-shot data ingestion from all configured sources.

**Response:**
```json
{
  "message": "Ingestion completed",
  "events_processed": 50,
  "events_stored": 45
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/ingest/one-shot
```

---

### Query Events

```http
GET /events?sw_lat={lat}&sw_lng={lng}&ne_lat={lat}&ne_lng={lng}&since_hours={hours}
```

Get safety events within a bounding box.

**Query Parameters:**
- `sw_lat`, `sw_lng` - Southwest corner of bounding box
- `ne_lat`, `ne_lng` - Northeast corner of bounding box
- `since_hours` - Time window in hours (default: 24)

**Response:**
```json
{
  "events": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "source": "rss:https://example.com/feed",
      "title": "Traffic Accident on Broadway",
      "text": "Multi-vehicle accident reported...",
      "timestamp": "2024-01-18T10:30:00",
      "coordinates": {
        "lat": 40.7580,
        "lng": -73.9857
      },
      "safety_score": 65.5,
      "event_type": "accident",
      "severity": 7,
      "urgency": 60,
      "address_hint": "Broadway near Times Square",
      "notes": "Emergency services on scene"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl "http://localhost:8000/events?sw_lat=40.7&sw_lng=-74.0&ne_lat=40.8&ne_lng=-73.9&since_hours=24"
```

---

### Calculate Route

```http
POST /route
Content-Type: application/json
```

Calculate a route with safety analysis.

**Request Body:**
```json
{
  "start": {
    "lat": 40.7580,
    "lng": -73.9857
  },
  "end": {
    "lat": 40.7829,
    "lng": -73.9654
  },
  "mode": "driving",
  "alpha": 0.5,
  "beta": 0.5,
  "preference": "safest"
}
```

**Parameters:**
- `start`, `end` - Start and end coordinates
- `mode` - Travel mode: `driving`, `walking`, `bicycling`, `transit`
- `alpha` - Weight for distance (0-1)
- `beta` - Weight for risk (0-1)
- `preference` - Route preference: `fastest` or `safest`

**Response:**
```json
{
  "route": { /* Google Directions API route object */ },
  "distance_meters": 5000,
  "duration_seconds": 600,
  "aggregate_risk": 35.5,
  "event_count": 3,
  "preference": "safest",
  "polyline": "encoded_polyline_string"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/route \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 40.7580, "lng": -73.9857},
    "end": {"lat": 40.7829, "lng": -73.9654},
    "mode": "driving",
    "alpha": 0.5,
    "beta": 0.5,
    "preference": "safest"
  }'
```

---

## 🧮 Safety Scoring Algorithm

### Event Safety Score (0-100)

The safety score represents the risk level, where **higher score = higher risk**.

```python
# Step 1: Severity Score
severity_score = (LLM_severity / 10) × 100

# Step 2: Recency Decay (exponential, 24-hour half-life)
hours_since = (current_time - event_timestamp) / 3600
decay = exp(-hours_since / 24)

# Step 3: Keyword Impact
keyword_impact = 0
if high_risk_keywords:  # shooting, murder, fire, etc.
    keyword_impact += 15
if medium_risk_keywords:  # assault, robbery, accident, etc.
    keyword_impact += 8

# Step 4: Raw Score
raw_score = severity_score × decay + keyword_impact

# Step 5: Normalization
normalized_score = min(100, max(0, raw_score))
```

### Route Aggregate Risk

```python
# For each point along route:
aggregate_risk = Σ (event_safety_score / distance_to_route²)

# Where distance is measured from route point to event location
```

### Route Selection

```python
# Normalize all routes to 0-1 scale
normalized_distance = (distance - min_distance) / (max_distance - min_distance)
normalized_risk = (risk - min_risk) / (max_risk - min_risk)

# Combined score
route_score = α × normalized_distance + β × normalized_risk

# Select route with minimum score
selected_route = argmin(route_score)
```

**Default weights:**
- α (distance weight) = 0.5
- β (risk weight) = 0.5

---

## 💻 Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **Python 3.11** - Core language
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **OpenAI API** - LLM analysis
- **BeautifulSoup4** - HTML parsing
- **Feedparser** - RSS parsing
- **Polyline** - Google polyline decoding
- **APScheduler** - Background job scheduling

### Frontend
- **React 18** - UI framework
- **@react-google-maps/api** - Google Maps integration
- **Modern CSS** - Glassmorphic design

### Database
- **MongoDB 7.0** - Document database with geospatial indexing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

### External APIs
- **OpenAI GPT-3.5-turbo** - Event analysis
- **Google Geocoding API** - Address resolution
- **Google Directions API** - Route planning
- **Google Maps JavaScript API** - Map visualization

---

## 🛠️ Development

### Running Tests

```bash
docker-compose exec backend python -m unittest backend.tests.test_scoring
```

### Backend Development

The backend uses hot-reload. Changes to Python files will automatically reload the server.

```bash
# View backend logs
docker-compose logs -f backend

# Access backend container
docker-compose exec backend bash
```

### Frontend Development

The frontend uses Create React App with hot-reload. Changes will automatically refresh the browser.

```bash
# View frontend logs
docker-compose logs -f frontend

# Access frontend container
docker-compose exec frontend sh
```

### Database Access

```bash
# Access MongoDB shell
docker-compose exec mongo mongosh urbanpulse

# Count documents
db.events.countDocuments()

# View recent events
db.events.find().sort({timestamp: -1}).limit(5).pretty()
```

---

## 📊 Project Structure

```
urban-pulse/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application & routes
│   │   ├── db.py                # MongoDB operations
│   │   ├── scraper.py           # Data scraping (RSS, Reddit, HTML)
│   │   ├── llm.py               # LLM analysis & fallback
│   │   ├── geocode.py           # Google Geocoding wrapper
│   │   ├── scoring.py           # Safety scoring algorithms
│   │   └── scheduler.py         # Background job scheduler
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── seed_demo.py         # Demo data seeder
│   ├── tests/
│   │   └── test_scoring.py      # Unit tests
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.js               # Main React component
│   │   ├── App.css              # Glassmorphic styling
│   │   ├── index.js             # React entry point
│   │   └── index.css            # Global styles
│   ├── public/
│   │   └── index.html           # HTML template
│   ├── package.json             # Node dependencies
│   └── Dockerfile               # Frontend container
├── docker-compose.yml           # Multi-container orchestration
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🔧 Configuration

### RSS Feeds

Edit `backend/app/scraper.py`:

```python
rss_feeds = [
    "https://www.nyc.gov/site/nypd/news/rss-feed.page",
    "https://feeds.feedburner.com/your-city-news",
    # Add more feeds
]
```

### Reddit Subreddits

Edit `backend/app/scraper.py`:

```python
reddit_articles = scrape_reddit_rss("yourcity")  # e.g., "nyc", "sanfrancisco"
```

### Police Blotters

Edit `backend/app/scraper.py`:

```python
police_blotter_urls = [
    "https://example.com/police-blotter",
    # Add more URLs
]
```

### Safety Score Weights

Edit `backend/app/scoring.py` to adjust:
- Recency decay rate (default: 24-hour half-life)
- Keyword impact values
- Normalization bounds

---

## ❓ Troubleshooting

### API Keys Not Working

- Ensure `.env` file exists in project root
- Check that keys are **not wrapped in quotes**
- Verify API keys have necessary permissions enabled
- Restart containers after changing `.env`: `docker-compose down && docker-compose up --build`

### No Events Showing

1. **Ingest data:**
   ```bash
   curl -X POST http://localhost:8000/ingest/one-shot
   ```

2. **Or seed demo data:**
   ```bash
   docker-compose exec backend python -m app.scripts.seed_demo
   ```

3. **Check MongoDB:**
   ```bash
   docker-compose exec mongo mongosh urbanpulse --eval "db.events.countDocuments()"
   ```

### Frontend Not Loading Map

- Verify `REACT_APP_GOOGLE_MAPS_API_KEY` is set in `.env`
- Check browser console (F12) for errors
- Ensure Google Maps API has "Maps JavaScript API" enabled
- Check for HTTP referrer restrictions in Google Cloud Console

### Geocoding Failing

- Check Google Cloud Console for API quotas
- Ensure "Geocoding API" is enabled
- Verify API key has geocoding permissions
- Check for rate limiting

### Docker Issues

```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build

# View logs
docker-compose logs -f

# Check container status
docker-compose ps
```

---

## 🎯 Use Cases

### 1. Night Shift Workers
Navigate safely during late hours with real-time risk assessment.

### 2. Students & Campus Safety
Universities can deploy for student safety during night walks.

### 3. Delivery Drivers
Optimize routes considering both speed and safety.

### 4. Tourists
Unfamiliar with the area? Get safety-aware navigation.

### 5. Ride-Sharing Services
Integrate safety scoring into driver apps.

### 6. City Planners
Analyze safety patterns and allocate resources effectively.

### 7. Real Estate
Provide safety insights for property seekers.

---

## ⚠️ Disclaimer

**Urban Pulse is a demonstration project built for hackathons.**

- ⚠️ Safety scores are **estimates** based on aggregated public data
- ⚠️ Route recommendations are **suggestions only**, not guarantees
- ⚠️ Data may be incomplete, outdated, or inaccurate
- ⚠️ Users should exercise their own judgment and follow all applicable laws
- ⚠️ We are **not liable** for any incidents that may occur on recommended routes

**For production use**, additional measures are required:
- Legal review and terms of service
- Data accuracy validation
- Insurance coverage
- Regular data source verification
- User consent and acknowledgment of limitations

This system is designed to **inform**, not replace, user judgment.

---

## 👩‍💻 Author

<div align="center">

### Made with ❤️ by **Vijayshree Pathak**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Vijayshree_Vaibhav-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vijayshreevaibhav/)
[![Portfolio](https://img.shields.io/badge/Portfolio-vijayshreepathak.netlify.app-FF6B6B?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vijayshreepathak.netlify.app/)
[![GitHub](https://img.shields.io/badge/GitHub-vijayshreepathak-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/vijayshreepathak)

#### 🏆 Achievements
- 👑 **AIR 1** - StartupThon 2025
- 🏆 **8× Winner** - Hackathons
- 💎 **#1 Pan India** - DSA (10×)
- 📜 **2× Patent Holder**
- 👥 **10K+ LinkedIn** Followers
- 🎓 **1000+ Students** Mentored

#### 💼 Expertise
Production AI Systems • RAG Pipelines • Low-Latency Trading • Full-Stack Development • Cloud Architecture • Mentorship

---

### 🌟 If you found this project helpful, please give it a star!

[![GitHub stars](https://img.shields.io/github/stars/vijayshreepathak/Urban-Pulse?style=social)](https://github.com/vijayshreepathak/Urban-Pulse)

</div>

---

## 📄 License

This project is created for **hackathon and educational purposes**.

Feel free to use, modify, and distribute with proper attribution.

---

## 🙏 Acknowledgments

- OpenAI for GPT-3.5-turbo API
- Google Maps Platform for APIs
- MongoDB for database technology
- FastAPI and React communities
- All open-source contributors

---

<div align="center">

**Urban Pulse** • Smart Safety • Intelligent Routing • Real-Time Protection

[⬆ Back to Top](#-urban-pulse)

</div>
