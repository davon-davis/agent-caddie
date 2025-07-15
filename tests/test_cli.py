import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from agent_caddie.cli import cli


class TestCLIUpdate:
    """Test the update command functionality."""
    
    @patch('agent_caddie.cli.text')
    @patch('agent_caddie.cli.save_club_distances')
    def test_update_command_success(self, mock_save, mock_text):
        """Test successful club distance update."""
        runner = CliRunner()
        
        # Mock text inputs for all clubs
        mock_text.side_effect = [
            MagicMock(ask=lambda: "250"),  # Driver
            MagicMock(ask=lambda: ""),     # 3-Wood (skip)
            MagicMock(ask=lambda: "200"),  # 5-Wood
            MagicMock(ask=lambda: ""),     # 3-Iron (skip)
            MagicMock(ask=lambda: "180"),  # 4-Iron
            MagicMock(ask=lambda: "160"),  # 5-Iron
            MagicMock(ask=lambda: "150"),  # 6-Iron
            MagicMock(ask=lambda: "140"),  # 7-Iron
            MagicMock(ask=lambda: "130"),  # 8-Iron
            MagicMock(ask=lambda: "120"),  # 9-Iron
            MagicMock(ask=lambda: "110"),  # Pitching Wedge
            MagicMock(ask=lambda: "90"),   # Sand Wedge
            MagicMock(ask=lambda: "80"),   # 48°
            MagicMock(ask=lambda: "75"),   # 50°
            MagicMock(ask=lambda: "70"),   # 52°
            MagicMock(ask=lambda: "65"),   # 54°
            MagicMock(ask=lambda: "60"),   # 56°
            MagicMock(ask=lambda: "55"),   # 58°
            MagicMock(ask=lambda: "50"),   # 60°
        ]
        
        result = runner.invoke(cli, ['update', '--user-id', 'user123'])
        
        assert result.exit_code == 0
        mock_save.assert_called_once()
        
        # Verify the saved entries
        saved_entries = mock_save.call_args[0][0]
        assert len(saved_entries) == 17  # 19 clubs minus 2 skipped
        
        # Check a few specific entries
        driver_entry = next(e for e in saved_entries if e["club"] == "Driver")
        assert driver_entry["user_id"] == "user123"
        assert driver_entry["distance"] == 250.0
        
        iron_entry = next(e for e in saved_entries if e["club"] == "7-Iron")
        assert iron_entry["distance"] == 140.0
    
    @patch('agent_caddie.cli.text')
    @patch('agent_caddie.cli.save_club_distances')
    def test_update_command_invalid_input(self, mock_save, mock_text):
        """Test club distance update with invalid input."""
        runner = CliRunner()
        
        # Mock text inputs with invalid data
        mock_text.side_effect = [
            MagicMock(ask=lambda: "250"),  # Driver
            MagicMock(ask=lambda: "invalid"),  # 3-Wood (invalid)
            MagicMock(ask=lambda: "200"),  # 5-Wood
            MagicMock(ask=lambda: "abc"),  # 3-Iron (invalid)
            MagicMock(ask=lambda: "180"),  # 4-Iron
            MagicMock(ask=lambda: ""),     # 5-Iron (skip)
            MagicMock(ask=lambda: "160"),  # 6-Iron
            MagicMock(ask=lambda: "150"),  # 7-Iron
            MagicMock(ask=lambda: "140"),  # 8-Iron
            MagicMock(ask=lambda: "130"),  # 9-Iron
            MagicMock(ask=lambda: "120"),  # Pitching Wedge
            MagicMock(ask=lambda: "110"),  # Sand Wedge
            MagicMock(ask=lambda: "100"),  # 48°
            MagicMock(ask=lambda: "95"),   # 50°
            MagicMock(ask=lambda: "90"),   # 52°
            MagicMock(ask=lambda: "85"),   # 54°
            MagicMock(ask=lambda: "80"),   # 56°
            MagicMock(ask=lambda: "75"),   # 58°
            MagicMock(ask=lambda: "70"),   # 60°
        ]
        
        result = runner.invoke(cli, ['update', '--user-id', 'user123'])
        
        assert result.exit_code == 0
        mock_save.assert_called_once()
        
        # Verify the saved entries (should exclude invalid inputs)
        saved_entries = mock_save.call_args[0][0]
        assert len(saved_entries) == 16  # 19 clubs minus 3 invalid/skipped
        
        # Verify no invalid entries were saved
        for entry in saved_entries:
            assert isinstance(entry["distance"], float)
    
    @patch('agent_caddie.cli.text')
    @patch('agent_caddie.cli.save_club_distances')
    def test_update_command_all_skipped(self, mock_save, mock_text):
        """Test club distance update when all clubs are skipped."""
        runner = CliRunner()
        
        # Mock all text inputs as empty (skipped)
        mock_text.side_effect = [MagicMock(ask=lambda: "")] * 19
        
        result = runner.invoke(cli, ['update', '--user-id', 'user123'])
        
        assert result.exit_code == 0
        mock_save.assert_not_called()
        assert "No distances entered" in result.output
    
    def test_update_command_missing_user_id(self):
        """Test update command without required user-id."""
        runner = CliRunner()
        result = runner.invoke(cli, ['update'])
        
        assert result.exit_code != 0
        assert "Missing option '--user-id'" in result.output


class TestCLIShot:
    """Test the shot command functionality."""
    
    @patch('agent_caddie.cli.record_shot_result')
    @patch('agent_caddie.cli.save_shot')
    @patch('agent_caddie.cli.get_similar_shots')
    @patch('agent_caddie.cli.build_prompt')
    @patch('agent_caddie.cli.ask_shot_details')
    @patch('agent_caddie.cli.compute_effective_distance')
    @patch('agent_caddie.cli.openai')
    def test_shot_command_success(self, mock_openai, mock_compute, mock_ask, 
                                 mock_build, mock_get_similar, mock_save, mock_record):
        """Test successful shot recommendation."""
        runner = CliRunner()
        
        # Mock shot details
        mock_scenario = {
            "distance": 150,
            "lie": "Rough",
            "ball_pos": "Above feet",
            "wind": {"direction": "Headwind", "speed": 10},
            "elevation": "Uphill",
            "scenario_text": "150y, lie=Rough, ball_pos=Above feet, wind=10mph Headwind, elev=Uphill"
        }
        mock_ask.return_value = mock_scenario
        
        # Mock effective distance calculation
        mock_compute.return_value = 155
        
        # Mock similar shots
        mock_past_shots = [
            {"recommended_club": "7-Iron", "carried": 152, "result": "perfect"}
        ]
        mock_get_similar.return_value = mock_past_shots
        
        # Mock prompt building
        mock_prompt = [
            {"role": "system", "content": "You're a golf caddie"},
            {"role": "user", "content": "What club?"}
        ]
        mock_build.return_value = mock_prompt
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="7-Iron"))]
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Mock shot result recording
        mock_result = {
            "carried": 152,
            "error": 2,
            "result": "perfect",
            "cause": None
        }
        mock_record.return_value = mock_result
        
        result = runner.invoke(cli, ['shot', '--user-id', 'user123'])
        
        assert result.exit_code == 0
        assert "7-Iron" in result.output
        assert "Shot logged" in result.output
        
        # Verify all functions were called correctly
        mock_ask.assert_called_once()
        mock_compute.assert_called_once_with(mock_scenario)
        mock_get_similar.assert_called_once_with(mock_scenario["scenario_text"])
        mock_build.assert_called_once_with(mock_scenario, mock_past_shots)
        mock_openai.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=mock_prompt
        )
        mock_record.assert_called_once_with(mock_scenario)
        mock_save.assert_called_once()
        
        # Verify the saved shot data
        saved_shot = mock_save.call_args[0][0]
        assert saved_shot["user_id"] == "user123"
        assert saved_shot["recommended_club"] == "7-Iron"
        assert saved_shot["carried"] == 152
        assert saved_shot["error"] == 2
        assert saved_shot["result"] == "perfect"
    
    @patch('agent_caddie.cli.record_shot_result')
    @patch('agent_caddie.cli.save_shot')
    @patch('agent_caddie.cli.get_similar_shots')
    @patch('agent_caddie.cli.build_prompt')
    @patch('agent_caddie.cli.ask_shot_details')
    @patch('agent_caddie.cli.compute_effective_distance')
    @patch('agent_caddie.cli.openai')
    def test_shot_command_no_recommendation(self, mock_openai, mock_compute, mock_ask,
                                           mock_build, mock_get_similar, mock_save, mock_record):
        """Test shot command when no recommendation is returned."""
        runner = CliRunner()
        
        mock_scenario = {
            "distance": 150,
            "lie": "Fairway",
            "wind": {"direction": "None", "speed": 0},
            "elevation": "Level",
            "scenario_text": "150y, lie=Fairway"
        }
        mock_ask.return_value = mock_scenario
        mock_compute.return_value = 150
        mock_get_similar.return_value = []
        mock_build.return_value = [{"role": "system", "content": "test"}]
        
        # Mock OpenAI response with no content
        mock_response = MagicMock()
        mock_response.choices = []
        mock_openai.chat.completions.create.return_value = mock_response
        
        mock_result = {"carried": 150, "error": 0, "result": "perfect", "cause": None}
        mock_record.return_value = mock_result
        
        result = runner.invoke(cli, ['shot', '--user-id', 'user123'])
        
        assert result.exit_code == 0
        assert "No recommendation" in result.output
    
    @patch('agent_caddie.cli.record_shot_result')
    @patch('agent_caddie.cli.save_shot')
    @patch('agent_caddie.cli.get_similar_shots')
    @patch('agent_caddie.cli.build_prompt')
    @patch('agent_caddie.cli.ask_shot_details')
    @patch('agent_caddie.cli.compute_effective_distance')
    @patch('agent_caddie.cli.openai')
    def test_shot_command_empty_response(self, mock_openai, mock_compute, mock_ask,
                                       mock_build, mock_get_similar, mock_save, mock_record):
        """Test shot command with empty OpenAI response."""
        runner = CliRunner()
        
        mock_scenario = {
            "distance": 150,
            "lie": "Fairway",
            "wind": {"direction": "None", "speed": 0},
            "elevation": "Level",
            "scenario_text": "150y, lie=Fairway"
        }
        mock_ask.return_value = mock_scenario
        mock_compute.return_value = 150
        mock_get_similar.return_value = []
        mock_build.return_value = [{"role": "system", "content": "test"}]
        
        # Mock OpenAI response with empty content
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=""))]
        mock_openai.chat.completions.create.return_value = mock_response
        
        mock_result = {"carried": 150, "error": 0, "result": "perfect", "cause": None}
        mock_record.return_value = mock_result
        
        result = runner.invoke(cli, ['shot', '--user-id', 'user123'])
        
        assert result.exit_code == 0
        assert "No recommendation" in result.output
    
    def test_shot_command_missing_user_id(self):
        """Test shot command without required user-id."""
        runner = CliRunner()
        result = runner.invoke(cli, ['shot'])
        
        assert result.exit_code != 0
        assert "Missing option '--user-id'" in result.output


class TestCLIGeneral:
    """Test general CLI functionality."""
    
    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "V-Caddie CLI" in result.output
        assert "update" in result.output
        assert "shot" in result.output
    
    def test_update_help(self):
        """Test update command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['update', '--help'])
        
        assert result.exit_code == 0
        assert "Record or update your average carry distance" in result.output
        assert "--user-id" in result.output
    
    def test_shot_help(self):
        """Test shot command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['shot', '--help'])
        
        assert result.exit_code == 0
        assert "Get a club recommendation" in result.output
        assert "--user-id" in result.output 