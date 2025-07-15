import pytest
from unittest.mock import patch, MagicMock
from agent_caddie.db import save_club_distances, save_shot, get_similar_shots


class TestSaveClubDistances:
    """Test club distances saving functionality."""
    
    @patch('agent_caddie.db.supabase')
    def test_save_club_distances_single_entry(self, mock_supabase):
        """Test saving a single club distance entry."""
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = mock_execute
        
        entries = [{
            "user_id": "user123",
            "club": "7-Iron",
            "distance": 150.0
        }]
        
        save_club_distances(entries)
        
        mock_supabase.table.assert_called_once_with("club_distances")
        mock_table.upsert.assert_called_once_with(entries, on_conflict="user_id,club")
        mock_upsert.execute.assert_called_once()
    
    @patch('agent_caddie.db.supabase')
    def test_save_club_distances_multiple_entries(self, mock_supabase):
        """Test saving multiple club distance entries."""
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = mock_execute
        
        entries = [
            {"user_id": "user123", "club": "Driver", "distance": 250.0},
            {"user_id": "user123", "club": "7-Iron", "distance": 150.0},
            {"user_id": "user123", "club": "Pitching Wedge", "distance": 100.0}
        ]
        
        save_club_distances(entries)
        
        mock_supabase.table.assert_called_once_with("club_distances")
        mock_table.upsert.assert_called_once_with(entries, on_conflict="user_id,club")
        mock_upsert.execute.assert_called_once()
    
    @patch('agent_caddie.db.supabase')
    def test_save_club_distances_empty_list(self, mock_supabase):
        """Test saving empty list of club distances."""
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = mock_execute
        
        save_club_distances([])
        
        mock_supabase.table.assert_called_once_with("club_distances")
        mock_table.upsert.assert_called_once_with([], on_conflict="user_id,club")
        mock_upsert.execute.assert_called_once()


class TestSaveShot:
    """Test shot saving functionality."""
    
    @patch('agent_caddie.db.get_embedding')
    @patch('agent_caddie.db.supabase')
    def test_save_shot_normal_shot(self, mock_supabase, mock_get_embedding):
        """Test saving a normal shot (not mis-hit)."""
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute
        mock_get_embedding.return_value = mock_embedding
        
        shot_entry = {
            "user_id": "user123",
            "scenario_text": "150y, lie=Rough, ball_pos=Above feet, wind=10mph Headwind, elev=Uphill",
            "distance": 150,
            "lie": "Rough",
            "ball_pos": "Above feet",
            "wind": {"direction": "Headwind", "speed": 10},
            "elevation": "Uphill",
            "effective_dist": 155,
            "recommended_club": "7-Iron",
            "carried": 152,
            "error": 2,
            "result": "perfect",
            "cause": None
        }
        
        save_shot(shot_entry)
        
        # Verify embedding was generated
        mock_get_embedding.assert_called_once_with(shot_entry["scenario_text"])
        
        # Verify database insert
        mock_supabase.table.assert_called_once_with("shots")
        mock_table.insert.assert_called_once()
        
        # Verify the insert call arguments
        insert_call_args = mock_table.insert.call_args[0][0]
        assert insert_call_args["user_id"] == "user123"
        assert insert_call_args["scenario_text"] == shot_entry["scenario_text"]
        assert insert_call_args["distance"] == 150
        assert insert_call_args["lie"] == "Rough"
        assert insert_call_args["ball_pos"] == "Above feet"
        assert insert_call_args["wind_dir"] == "Headwind"
        assert insert_call_args["wind_speed"] == 10
        assert insert_call_args["elevation"] == "Uphill"
        assert insert_call_args["effective_dist"] == 155
        assert insert_call_args["recommended_club"] == "7-Iron"
        assert insert_call_args["carried"] == 152
        assert insert_call_args["error"] == 2
        assert insert_call_args["result"] == "perfect"
        assert insert_call_args["cause"] is None
        assert insert_call_args["embedding"] == mock_embedding
    
    @patch('agent_caddie.db.get_embedding')
    @patch('agent_caddie.db.supabase')
    def test_save_shot_mis_hit_shot(self, mock_supabase, mock_get_embedding):
        """Test that mis-hit shots are not saved."""
        shot_entry = {
            "user_id": "user123",
            "scenario_text": "150y, lie=Rough",
            "distance": 150,
            "lie": "Rough",
            "ball_pos": "Level",
            "wind": {"direction": "None", "speed": 0},
            "elevation": "Level",
            "effective_dist": 150,
            "recommended_club": "7-Iron",
            "carried": 140,
            "error": -10,
            "result": "too short",
            "cause": "Mis-hit"
        }
        
        save_shot(shot_entry)
        
        # Verify that no database operations were performed
        mock_supabase.table.assert_not_called()
        mock_get_embedding.assert_not_called()
    
    @patch('agent_caddie.db.get_embedding')
    @patch('agent_caddie.db.supabase')
    def test_save_shot_with_cause(self, mock_supabase, mock_get_embedding):
        """Test saving a shot with a cause."""
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()
        mock_embedding = [0.5, -0.3, 0.8]
        
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute
        mock_get_embedding.return_value = mock_embedding
        
        shot_entry = {
            "user_id": "user123",
            "scenario_text": "200y, lie=Fairway",
            "distance": 200,
            "lie": "Fairway",
            "ball_pos": "Level",
            "wind": {"direction": "Tailwind", "speed": 5},
            "elevation": "Level",
            "effective_dist": 195,
            "recommended_club": "5-Iron",
            "carried": 210,
            "error": 10,
            "result": "too long",
            "cause": "Club selection"
        }
        
        save_shot(shot_entry)
        
        # Verify the insert call arguments
        insert_call_args = mock_table.insert.call_args[0][0]
        assert insert_call_args["cause"] == "Club selection"
        assert insert_call_args["embedding"] == mock_embedding


class TestGetSimilarShots:
    """Test similar shots retrieval functionality."""
    
    @patch('agent_caddie.db.get_embedding')
    @patch('agent_caddie.db.supabase')
    def test_get_similar_shots_success(self, mock_supabase, mock_get_embedding):
        """Test successful retrieval of similar shots."""
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_similar_shots = [
            {
                "id": 1,
                "recommended_club": "7-Iron",
                "carried": 152,
                "result": "perfect"
            },
            {
                "id": 2,
                "recommended_club": "6-Iron",
                "carried": 165,
                "result": "too long"
            }
        ]
        
        mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=mock_similar_shots)
        mock_get_embedding.return_value = mock_embedding
        
        scenario_text = "150y, lie=Rough, ball_pos=Above feet"
        result = get_similar_shots(scenario_text)
        
        # Verify embedding was generated
        mock_get_embedding.assert_called_once_with(scenario_text)
        
        # Verify RPC call
        mock_supabase.rpc.assert_called_once_with(
            "match_shots",
            {"query_embedding": mock_embedding, "match_count": 3}
        )
        mock_rpc.execute.assert_called_once()
        
        # Verify result
        assert result == mock_similar_shots
    
    @patch('agent_caddie.db.get_embedding')
    @patch('agent_caddie.db.supabase')
    def test_get_similar_shots_custom_k(self, mock_supabase, mock_get_embedding):
        """Test retrieval with custom k value."""
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        mock_embedding = [0.1, 0.2, 0.3]
        
        mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=[])
        mock_get_embedding.return_value = mock_embedding
        
        scenario_text = "200y, lie=Fairway"
        result = get_similar_shots(scenario_text, k=5)
        
        # Verify RPC call with custom k
        mock_supabase.rpc.assert_called_once_with(
            "match_shots",
            {"query_embedding": mock_embedding, "match_count": 5}
        )
        
        assert result == []
    
    @patch('agent_caddie.db.get_embedding')
    @patch('agent_caddie.db.supabase')
    def test_get_similar_shots_no_results(self, mock_supabase, mock_get_embedding):
        """Test retrieval when no similar shots are found."""
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        mock_embedding = [0.1, 0.2, 0.3]
        
        mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=None)
        mock_get_embedding.return_value = mock_embedding
        
        scenario_text = "300y, lie=Rough"
        result = get_similar_shots(scenario_text)
        
        assert result == []
    
    @patch('agent_caddie.db.get_embedding')
    @patch('agent_caddie.db.supabase')
    def test_get_similar_shots_empty_string(self, mock_supabase, mock_get_embedding):
        """Test retrieval with empty scenario text."""
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        mock_embedding = [0.0, 0.0, 0.0]
        
        mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = MagicMock(data=[])
        mock_get_embedding.return_value = mock_embedding
        
        result = get_similar_shots("")
        
        mock_get_embedding.assert_called_once_with("")
        assert result == [] 