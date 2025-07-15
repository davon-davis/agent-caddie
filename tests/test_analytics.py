import pytest
from unittest.mock import patch, MagicMock
from agent_caddie.analytics import wind_adj, compute_effective_distance, record_shot_result


class TestWindAdjustment:
    """Test wind adjustment calculations."""
    
    def test_headwind_adjustment(self):
        """Test headwind increases effective distance."""
        result = wind_adj("Headwind", 10)
        assert result == 5.0  # 10 * 0.5
    
    def test_tailwind_adjustment(self):
        """Test tailwind decreases effective distance."""
        result = wind_adj("Tailwind", 10)
        assert result == -5.0  # -10 * 0.5
    
    def test_crosswind_no_adjustment(self):
        """Test crosswind has no effect on distance."""
        result = wind_adj("Left→Right", 10)
        assert result == 0
    
    def test_no_wind_no_adjustment(self):
        """Test no wind has no effect on distance."""
        result = wind_adj("None", 10)
        assert result == 0
    
    def test_zero_wind_speed(self):
        """Test zero wind speed results in zero adjustment."""
        result = wind_adj("Headwind", 0)
        assert result == 0


class TestEffectiveDistance:
    """Test effective distance calculations."""
    
    def test_basic_distance_no_adjustments(self):
        """Test distance with no lie or wind adjustments."""
        scenario = {
            "distance": 150,
            "lie": "Fairway",
            "wind": {"direction": "None", "speed": 0}
        }
        result = compute_effective_distance(scenario)
        assert result == 150
    
    def test_rough_lie_adjustment(self):
        """Test rough lie adds 8 yards."""
        scenario = {
            "distance": 150,
            "lie": "Rough",
            "wind": {"direction": "None", "speed": 0}
        }
        result = compute_effective_distance(scenario)
        assert result == 158  # 150 + 8
    
    def test_sand_lie_adjustment(self):
        """Test sand lie adds 12 yards."""
        scenario = {
            "distance": 150,
            "lie": "Sand / Bunker",
            "wind": {"direction": "None", "speed": 0}
        }
        result = compute_effective_distance(scenario)
        assert result == 162  # 150 + 12
    
    def test_above_feet_adjustment(self):
        """Test above feet adds 5 yards."""
        scenario = {
            "distance": 150,
            "lie": "Above feet",
            "wind": {"direction": "None", "speed": 0}
        }
        result = compute_effective_distance(scenario)
        assert result == 155  # 150 + 5
    
    def test_below_feet_adjustment(self):
        """Test below feet subtracts 5 yards."""
        scenario = {
            "distance": 150,
            "lie": "Below feet",
            "wind": {"direction": "None", "speed": 0}
        }
        result = compute_effective_distance(scenario)
        assert result == 145  # 150 - 5
    
    def test_headwind_adjustment(self):
        """Test headwind increases effective distance."""
        scenario = {
            "distance": 150,
            "lie": "Fairway",
            "wind": {"direction": "Headwind", "speed": 10}
        }
        result = compute_effective_distance(scenario)
        assert result == 155  # 150 + 5 (wind adjustment)
    
    def test_tailwind_adjustment(self):
        """Test tailwind decreases effective distance."""
        scenario = {
            "distance": 150,
            "lie": "Fairway",
            "wind": {"direction": "Tailwind", "speed": 10}
        }
        result = compute_effective_distance(scenario)
        assert result == 145  # 150 - 5 (wind adjustment)
    
    def test_combined_adjustments(self):
        """Test multiple adjustments applied together."""
        scenario = {
            "distance": 150,
            "lie": "Rough",
            "wind": {"direction": "Headwind", "speed": 10}
        }
        result = compute_effective_distance(scenario)
        assert result == 163  # 150 + 8 (rough) + 5 (headwind)
    
    def test_unknown_lie_no_adjustment(self):
        """Test unknown lie type has no adjustment."""
        scenario = {
            "distance": 150,
            "lie": "Unknown Lie",
            "wind": {"direction": "None", "speed": 0}
        }
        result = compute_effective_distance(scenario)
        assert result == 150


class TestRecordShotResult:
    """Test shot result recording functionality."""
    
    @patch('agent_caddie.analytics.text')
    @patch('agent_caddie.analytics.select')
    def test_perfect_shot(self, mock_select, mock_text):
        """Test perfect shot recording."""
        mock_text.return_value.ask.return_value = "150"
        mock_select.return_value.ask.return_value = None  # No cause needed for perfect shot
        
        scenario = {"distance": 150}
        result = record_shot_result(scenario)
        
        assert result["carried"] == 150.0
        assert result["error"] == 0.0
        assert result["result"] == "perfect"
        assert result["cause"] is None
    
    @patch('agent_caddie.analytics.text')
    @patch('agent_caddie.analytics.select')
    def test_shot_too_short(self, mock_select, mock_text):
        """Test shot that comes up short."""
        mock_text.return_value.ask.return_value = "140"
        mock_select.return_value.ask.return_value = "Mis-hit"
        
        scenario = {"distance": 150}
        result = record_shot_result(scenario)
        
        assert result["carried"] == 140.0
        assert result["error"] == -10.0
        assert result["result"] == "too short"
        assert result["cause"] == "Mis-hit"
    
    @patch('agent_caddie.analytics.text')
    @patch('agent_caddie.analytics.select')
    def test_shot_too_long(self, mock_select, mock_text):
        """Test shot that goes too far."""
        mock_text.return_value.ask.return_value = "160"
        mock_select.return_value.ask.return_value = "Club selection"
        
        scenario = {"distance": 150}
        result = record_shot_result(scenario)
        
        assert result["carried"] == 160.0
        assert result["error"] == 10.0
        assert result["result"] == "too long"
        assert result["cause"] == "Club selection"
    
    @patch('agent_caddie.analytics.text')
    @patch('agent_caddie.analytics.select')
    def test_close_shot_within_tolerance(self, mock_select, mock_text):
        """Test shot within 5 yard tolerance is considered perfect."""
        mock_text.return_value.ask.return_value = "153"
        mock_select.return_value.ask.return_value = None
        
        scenario = {"distance": 150}
        result = record_shot_result(scenario)
        
        assert result["carried"] == 153.0
        assert result["error"] == 3.0
        assert result["result"] == "perfect"
        assert result["cause"] is None
    
    @patch('agent_caddie.analytics.text')
    @patch('agent_caddie.analytics.select')
    def test_negative_tolerance_shot(self, mock_select, mock_text):
        """Test shot within negative tolerance is considered perfect."""
        mock_text.return_value.ask.return_value = "147"
        mock_select.return_value.ask.return_value = None
        
        scenario = {"distance": 150}
        result = record_shot_result(scenario)
        
        assert result["carried"] == 147.0
        assert result["error"] == -3.0
        assert result["result"] == "perfect"
        assert result["cause"] is None 