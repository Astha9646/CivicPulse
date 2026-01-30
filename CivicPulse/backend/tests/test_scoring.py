"""Unit tests for safety scoring module."""
import unittest
from datetime import datetime, timedelta
from app.scoring import compute_score, haversine_distance


class TestScoring(unittest.TestCase):
    
    def test_compute_score_recent_high_severity(self):
        """Test score calculation for recent high-severity event."""
        event = {
            "severity": 9,
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "title": "Shooting incident",
            "text": "Shooting reported in downtown area"
        }
        score = compute_score(event)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertGreater(score, 50)  # High severity should yield high score
    
    def test_compute_score_old_event(self):
        """Test that old events have lower scores due to decay."""
        recent_event = {
            "severity": 7,
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "title": "Accident",
            "text": "Car accident"
        }
        old_event = {
            "severity": 7,
            "timestamp": datetime.utcnow() - timedelta(hours=48),
            "title": "Accident",
            "text": "Car accident"
        }
        
        recent_score = compute_score(recent_event)
        old_score = compute_score(old_event)
        
        self.assertGreater(recent_score, old_score)
    
    def test_compute_score_keyword_impact(self):
        """Test that high-risk keywords increase score."""
        event_with_keywords = {
            "severity": 5,
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "title": "Shooting incident",
            "text": "Shooting reported"
        }
        event_without_keywords = {
            "severity": 5,
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "title": "General incident",
            "text": "General report"
        }
        
        score_with = compute_score(event_with_keywords)
        score_without = compute_score(event_without_keywords)
        
        self.assertGreater(score_with, score_without)
    
    def test_compute_score_bounds(self):
        """Test that scores are always within 0-100 range."""
        test_cases = [
            {"severity": 1, "timestamp": datetime.utcnow()},
            {"severity": 10, "timestamp": datetime.utcnow()},
            {"severity": 5, "timestamp": datetime.utcnow() - timedelta(days=30)},
        ]
        
        for event_data in test_cases:
            event = {
                **event_data,
                "title": "Test",
                "text": "Test event"
            }
            score = compute_score(event)
            self.assertGreaterEqual(score, 0, f"Score {score} should be >= 0")
            self.assertLessEqual(score, 100, f"Score {score} should be <= 100")
    
    def test_haversine_distance(self):
        """Test Haversine distance calculation."""
        # Distance between NYC (40.7128, -74.0060) and Philadelphia (39.9526, -75.1652)
        # Should be approximately 95 km
        nyc_lat, nyc_lng = 40.7128, -74.0060
        philly_lat, philly_lng = 39.9526, -75.1652
        
        distance = haversine_distance(nyc_lat, nyc_lng, philly_lat, philly_lng)
        
        # Should be approximately 95,000 meters (allow 5% tolerance)
        expected = 95000
        self.assertAlmostEqual(distance, expected, delta=expected * 0.05)
        
        # Distance to self should be 0
        self.assertEqual(haversine_distance(nyc_lat, nyc_lng, nyc_lat, nyc_lng), 0)


if __name__ == "__main__":
    unittest.main()
