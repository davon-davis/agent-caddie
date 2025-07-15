import pytest
from unittest.mock import MagicMock


@pytest.fixture
def sample_scenario():
    """Sample golf scenario for testing."""
    return {
        "distance": 150,
        "lie": "Rough",
        "ball_pos": "Above feet",
        "wind": {"direction": "Headwind", "speed": 10},
        "elevation": "Uphill",
        "scenario_text": "150y, lie=Rough, ball_pos=Above feet, wind=10mph Headwind, elev=Uphill",
        "effective_dist": 155
    }


@pytest.fixture
def sample_past_shots():
    """Sample past shots for testing."""
    return [
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
        },
        {
            "id": 3,
            "recommended_club": "8-Iron",
            "carried": 140,
            "result": "too short"
        }
    ]


@pytest.fixture
def sample_club_distances():
    """Sample club distances for testing."""
    return [
        {"user_id": "user123", "club": "Driver", "distance": 250.0},
        {"user_id": "user123", "club": "7-Iron", "distance": 150.0},
        {"user_id": "user123", "club": "Pitching Wedge", "distance": 100.0}
    ]


@pytest.fixture
def sample_shot_result():
    """Sample shot result for testing."""
    return {
        "carried": 152,
        "error": 2,
        "result": "perfect",
        "cause": None
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response for testing."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="7-Iron"))]
    return mock_response


@pytest.fixture
def mock_embedding():
    """Mock embedding for testing."""
    return [0.1, 0.2, 0.3, 0.4, 0.5]


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_upsert = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    mock_rpc = MagicMock()
    
    mock_client.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert
    mock_table.insert.return_value = mock_insert
    mock_upsert.execute.return_value = mock_execute
    mock_insert.execute.return_value = mock_execute
    mock_client.rpc.return_value = mock_rpc
    mock_rpc.execute.return_value = MagicMock(data=[])
    
    return mock_client 