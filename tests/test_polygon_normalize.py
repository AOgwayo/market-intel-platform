import pytest
from datetime import datetime
from backend.app.ingestion.polygon_equities import PolygonEquitiesClient


class TestPolygonNormalization:
    """Tests for Polygon API response normalization."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = PolygonEquitiesClient(api_key="test_key")
    
    def test_normalize_polygon_response_success(self):
        """Test successful normalization of Polygon API response."""
        # Mock Polygon API response
        polygon_response = {
            "status": "OK",
            "results": [
                {
                    "t": 1640995200000,  # 2022-01-01 00:00:00 UTC in milliseconds
                    "o": 100.50,
                    "h": 101.25,
                    "l": 100.00,
                    "c": 100.75,
                    "v": 1500000,
                    "n": 1250
                },
                {
                    "t": 1640995260000,  # 2022-01-01 00:01:00 UTC in milliseconds
                    "o": 100.75,
                    "h": 102.00,
                    "l": 100.50,
                    "c": 101.50,
                    "v": 2000000,
                    "n": 1800
                }
            ]
        }
        
        normalized = self.client._normalize_polygon_response(
            polygon_response, "AAPL", "1m"
        )
        
        assert len(normalized) == 2
        
        # Check first bar
        first_bar = normalized[0]
        assert first_bar["symbol"] == "AAPL"
        assert first_bar["timestamp"] == datetime(2022, 1, 1, 0, 0, 0)
        assert first_bar["timeframe"] == "1m"
        assert first_bar["open"] == 100.50
        assert first_bar["high"] == 101.25
        assert first_bar["low"] == 100.00
        assert first_bar["close"] == 100.75
        assert first_bar["volume"] == 1500000
        assert first_bar["num_trades"] == 1250
        assert first_bar["source"] == "polygon"
        
        # Check second bar
        second_bar = normalized[1]
        assert second_bar["symbol"] == "AAPL"
        assert second_bar["timestamp"] == datetime(2022, 1, 1, 0, 1, 0)
        assert second_bar["close"] == 101.50
    
    def test_normalize_polygon_response_empty_results(self):
        """Test normalization with empty results."""
        polygon_response = {
            "status": "OK",
            "results": []
        }
        
        normalized = self.client._normalize_polygon_response(
            polygon_response, "AAPL", "1m"
        )
        
        assert normalized == []
    
    def test_normalize_polygon_response_no_results_key(self):
        """Test normalization with missing results key."""
        polygon_response = {
            "status": "OK"
        }
        
        normalized = self.client._normalize_polygon_response(
            polygon_response, "AAPL", "1m"
        )
        
        assert normalized == []
    
    def test_normalize_polygon_response_error_status(self):
        """Test normalization with error status."""
        polygon_response = {
            "status": "ERROR",
            "error": "API key not found",
            "results": []
        }
        
        normalized = self.client._normalize_polygon_response(
            polygon_response, "AAPL", "1m"
        )
        
        assert normalized == []
    
    def test_normalize_polygon_response_daily_timeframe(self):
        """Test normalization for daily timeframe."""
        polygon_response = {
            "status": "OK",
            "results": [
                {
                    "t": 1640995200000,
                    "o": 100.50,
                    "h": 105.25,
                    "l": 99.50,
                    "c": 104.75,
                    "v": 50000000,
                    "n": 45000
                }
            ]
        }
        
        normalized = self.client._normalize_polygon_response(
            polygon_response, "MSFT", "1d"
        )
        
        assert len(normalized) == 1
        bar = normalized[0]
        assert bar["symbol"] == "MSFT"
        assert bar["timeframe"] == "1d"
        assert bar["volume"] == 50000000
    
    def test_normalize_polygon_response_missing_trades_count(self):
        """Test normalization when trades count is missing."""
        polygon_response = {
            "status": "OK",
            "results": [
                {
                    "t": 1640995200000,
                    "o": 100.50,
                    "h": 101.25,
                    "l": 100.00,
                    "c": 100.75,
                    "v": 1500000
                    # Note: 'n' (num_trades) is missing
                }
            ]
        }
        
        normalized = self.client._normalize_polygon_response(
            polygon_response, "AAPL", "1m"
        )
        
        assert len(normalized) == 1
        bar = normalized[0]
        assert bar["num_trades"] is None
        assert bar["volume"] == 1500000
    
    def test_symbol_case_normalization(self):
        """Test that symbols are normalized to uppercase."""
        polygon_response = {
            "status": "OK",
            "results": [
                {
                    "t": 1640995200000,
                    "o": 100.50,
                    "h": 101.25,
                    "l": 100.00,
                    "c": 100.75,
                    "v": 1500000,
                    "n": 1250
                }
            ]
        }
        
        # Test with lowercase input symbol
        normalized = self.client._normalize_polygon_response(
            polygon_response, "aapl", "1m"
        )
        
        assert len(normalized) == 1
        assert normalized[0]["symbol"] == "AAPL"