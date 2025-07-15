import pytest
from unittest.mock import patch, MagicMock
from agent_caddie.prompts import ask_shot_details, build_prompt


class TestAskShotDetails:
    """Test shot details collection functionality."""
    
    @patch('agent_caddie.prompts.text')
    @patch('agent_caddie.prompts.select')
    def test_ask_shot_details_complete(self, mock_select, mock_text):
        """Test complete shot details collection."""
        # Mock the text inputs
        mock_text.side_effect = [
            MagicMock(ask=lambda: "150"),  # Distance
            MagicMock(ask=lambda: "10")    # Wind speed
        ]
        
        # Mock the select inputs
        mock_select.side_effect = [
            MagicMock(ask=lambda: "Rough"),           # Lie
            MagicMock(ask=lambda: "Above feet"),      # Ball position
            MagicMock(ask=lambda: "Uphill"),          # Elevation
            MagicMock(ask=lambda: "Headwind")         # Wind direction
        ]
        
        result = ask_shot_details()
        
        # Verify the structure
        assert result["distance"] == 150.0
        assert result["lie"] == "Rough"
        assert result["ball_pos"] == "Above feet"
        assert result["elevation"] == "Uphill"
        assert result["wind"]["direction"] == "Headwind"
        assert result["wind"]["speed"] == 10.0
        
        # Verify scenario text format
        expected_text = "150.0y, lie=Rough, ball_pos=Above feet, wind=10.0mph Headwind, elev=Uphill"
        assert result["scenario_text"] == expected_text
    
    @patch('agent_caddie.prompts.text')
    @patch('agent_caddie.prompts.select')
    def test_ask_shot_details_fairway_shot(self, mock_select, mock_text):
        """Test fairway shot details collection."""
        mock_text.side_effect = [
            MagicMock(ask=lambda: "200"),  # Distance
            MagicMock(ask=lambda: "5")     # Wind speed
        ]
        
        mock_select.side_effect = [
            MagicMock(ask=lambda: "Fairway"),         # Lie
            MagicMock(ask=lambda: "Level"),           # Ball position
            MagicMock(ask=lambda: "Level"),           # Elevation
            MagicMock(ask=lambda: "Tailwind")         # Wind direction
        ]
        
        result = ask_shot_details()
        
        assert result["distance"] == 200.0
        assert result["lie"] == "Fairway"
        assert result["ball_pos"] == "Level"
        assert result["elevation"] == "Level"
        assert result["wind"]["direction"] == "Tailwind"
        assert result["wind"]["speed"] == 5.0
        
        expected_text = "200.0y, lie=Fairway, ball_pos=Level, wind=5.0mph Tailwind, elev=Level"
        assert result["scenario_text"] == expected_text
    
    @patch('agent_caddie.prompts.text')
    @patch('agent_caddie.prompts.select')
    def test_ask_shot_details_sand_shot(self, mock_select, mock_text):
        """Test sand shot details collection."""
        mock_text.side_effect = [
            MagicMock(ask=lambda: "80"),   # Distance
            MagicMock(ask=lambda: "0")     # Wind speed
        ]
        
        mock_select.side_effect = [
            MagicMock(ask=lambda: "Sand / Bunker"),   # Lie
            MagicMock(ask=lambda: "Below feet"),      # Ball position
            MagicMock(ask=lambda: "Downhill"),        # Elevation
            MagicMock(ask=lambda: "None")             # Wind direction
        ]
        
        result = ask_shot_details()
        
        assert result["distance"] == 80.0
        assert result["lie"] == "Sand / Bunker"
        assert result["ball_pos"] == "Below feet"
        assert result["elevation"] == "Downhill"
        assert result["wind"]["direction"] == "None"
        assert result["wind"]["speed"] == 0.0
        
        expected_text = "80.0y, lie=Sand / Bunker, ball_pos=Below feet, wind=0.0mph None, elev=Downhill"
        assert result["scenario_text"] == expected_text


class TestBuildPrompt:
    """Test prompt building functionality."""
    
    def test_build_prompt_basic(self):
        """Test basic prompt building with no past shots."""
        scenario = {
            "distance": 150,
            "effective_dist": 155
        }
        past_shots = []
        
        result = build_prompt(scenario, past_shots)
        
        assert len(result) == 2
        assert result[0]["role"] == "system"
        # Get the actual content from the function to avoid quote character issues
        actual_content = result[0]["content"]
        assert "golf caddie balancing conditions and history" in actual_content
        
        expected_user_content = "Effective distance: 155 y (150 base + adjustments).\n\nSimilar past shots:\n\nGiven this, what club would you suggest?"
        assert result[1]["role"] == "user"
        assert result[1]["content"] == expected_user_content
    
    def test_build_prompt_with_past_shots(self):
        """Test prompt building with past shots included."""
        scenario = {
            "distance": 150,
            "effective_dist": 155
        }
        past_shots = [
            {
                "recommended_club": "7-Iron",
                "carried": 152,
                "result": "perfect"
            },
            {
                "recommended_club": "6-Iron",
                "carried": 165,
                "result": "too long"
            }
        ]
        
        result = build_prompt(scenario, past_shots)
        
        assert len(result) == 2
        assert result[0]["role"] == "system"
        
        user_content = result[1]["content"]
        assert "Effective distance: 155 y (150 base + adjustments)." in user_content
        assert "Similar past shots:" in user_content
        assert "- You took 7-Iron and carried 152y (perfect)." in user_content
        assert "- You took 6-Iron and carried 165y (too long)." in user_content
        assert "Given this, what club would you suggest?" in user_content
    
    def test_build_prompt_multiple_past_shots(self):
        """Test prompt building with multiple past shots."""
        scenario = {
            "distance": 200,
            "effective_dist": 210
        }
        past_shots = [
            {
                "recommended_club": "5-Iron",
                "carried": 205,
                "result": "perfect"
            },
            {
                "recommended_club": "4-Iron",
                "carried": 220,
                "result": "too long"
            },
            {
                "recommended_club": "6-Iron",
                "carried": 190,
                "result": "too short"
            }
        ]
        
        result = build_prompt(scenario, past_shots)
        
        user_content = result[1]["content"]
        assert "Effective distance: 210 y (200 base + adjustments)." in user_content
        assert "- You took 5-Iron and carried 205y (perfect)." in user_content
        assert "- You took 4-Iron and carried 220y (too long)." in user_content
        assert "- You took 6-Iron and carried 190y (too short)." in user_content
    
    def test_build_prompt_zero_effective_distance(self):
        """Test prompt building with zero effective distance."""
        scenario = {
            "distance": 0,
            "effective_dist": 0
        }
        past_shots = []
        
        result = build_prompt(scenario, past_shots)
        
        user_content = result[1]["content"]
        assert "Effective distance: 0 y (0 base + adjustments)." in user_content
    
    def test_build_prompt_negative_effective_distance(self):
        """Test prompt building with negative effective distance."""
        scenario = {
            "distance": 100,
            "effective_dist": -5
        }
        past_shots = []
        
        result = build_prompt(scenario, past_shots)
        
        user_content = result[1]["content"]
        assert "Effective distance: -5 y (100 base + adjustments)." in user_content 