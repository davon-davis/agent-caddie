import pytest
from unittest.mock import patch, MagicMock
from agent_caddie.embeddings import get_embedding


class TestGetEmbedding:
    """Test embedding generation functionality."""
    
    @patch('agent_caddie.embeddings.openai')
    def test_get_embedding_success(self, mock_openai):
        """Test successful embedding generation."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])]
        mock_openai.embeddings.create.return_value = mock_response
        
        result = get_embedding("Test scenario text")
        
        # Verify OpenAI was called correctly
        mock_openai.embeddings.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input="Test scenario text"
        )
        
        # Verify the result
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
    
    @patch('agent_caddie.embeddings.openai')
    def test_get_embedding_golf_scenario(self, mock_openai):
        """Test embedding generation for a golf scenario."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.5, -0.3, 0.8, -0.1, 0.2])]
        mock_openai.embeddings.create.return_value = mock_response
        
        scenario_text = "150y, lie=Rough, ball_pos=Above feet, wind=10mph Headwind, elev=Uphill"
        result = get_embedding(scenario_text)
        
        mock_openai.embeddings.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input=scenario_text
        )
        
        assert result == [0.5, -0.3, 0.8, -0.1, 0.2]
    
    @patch('agent_caddie.embeddings.openai')
    def test_get_embedding_empty_string(self, mock_openai):
        """Test embedding generation for empty string."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.0, 0.0, 0.0])]
        mock_openai.embeddings.create.return_value = mock_response
        
        result = get_embedding("")
        
        mock_openai.embeddings.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input=""
        )
        
        assert result == [0.0, 0.0, 0.0]
    
    @patch('agent_caddie.embeddings.openai')
    def test_get_embedding_long_text(self, mock_openai):
        """Test embedding generation for long text."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]  # Standard embedding size
        mock_openai.embeddings.create.return_value = mock_response
        
        long_text = "This is a very long golf scenario description with many details about the shot, the conditions, the wind, the lie, the ball position, and all the other factors that go into making a club selection decision." * 10
        
        result = get_embedding(long_text)
        
        mock_openai.embeddings.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input=long_text
        )
        
        assert len(result) == 1536
        assert all(val == 0.1 for val in result)
    
    @patch('agent_caddie.embeddings.openai')
    def test_get_embedding_special_characters(self, mock_openai):
        """Test embedding generation with special characters."""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.3, -0.7, 0.9])]
        mock_openai.embeddings.create.return_value = mock_response
        
        special_text = "150y, lie=Rough, ball_pos=Above feet, wind=10mph Headwind →, elev=Uphill"
        result = get_embedding(special_text)
        
        mock_openai.embeddings.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input=special_text
        )
        
        assert result == [0.3, -0.7, 0.9]
    
    @patch('agent_caddie.embeddings.openai')
    def test_get_embedding_multiple_calls(self, mock_openai):
        """Test multiple embedding generation calls."""
        # First call
        mock_response1 = MagicMock()
        mock_response1.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        
        # Second call
        mock_response2 = MagicMock()
        mock_response2.data = [MagicMock(embedding=[0.4, 0.5, 0.6])]
        
        mock_openai.embeddings.create.side_effect = [mock_response1, mock_response2]
        
        result1 = get_embedding("First scenario")
        result2 = get_embedding("Second scenario")
        
        # Verify both calls were made
        assert mock_openai.embeddings.create.call_count == 2
        assert result1 == [0.1, 0.2, 0.3]
        assert result2 == [0.4, 0.5, 0.6] 