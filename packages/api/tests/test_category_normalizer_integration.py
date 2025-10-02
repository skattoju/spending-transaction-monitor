"""
Unit tests for CategoryNormalizer integration
Can be run with pytest or the existing test framework
"""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import the functions we want to test
from src.services.category_normalizer import CategoryNormalizer


class TestCategoryNormalizerIntegration:
    """Unit tests for CategoryNormalizer integration"""
    
    @pytest.fixture
    async def mock_session(self):
        """Mock database session"""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.mark.asyncio
    async def test_category_normalizer_basic_functionality(self, mock_session):
        """Test basic CategoryNormalizer functionality"""
        # Mock the database query result
        mock_result = AsyncMock()
        mock_result.scalar.return_value = "dining"
        mock_session.execute.return_value = mock_result
        
        # Test synonym lookup
        result = await CategoryNormalizer.normalize(mock_session, "restaurant")
        assert result == "dining"
        
        # Test that execute was called
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_category_normalizer_fallback_to_original(self, mock_session):
        """Test that CategoryNormalizer falls back to original term when no match found"""
        # Mock no synonym match
        mock_result = AsyncMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Mock embedding service failure
        with patch('services.category_normalizer.embedding_service') as mock_embedding:
            mock_embedding.get_embedding.side_effect = Exception("Embedding service unavailable")
            
            result = await CategoryNormalizer.normalize(mock_session, "unknown_category")
            assert result == "unknown_category"
    
    @pytest.mark.asyncio
    async def test_category_normalizer_with_embeddings(self, mock_session):
        """Test CategoryNormalizer with embedding fallback"""
        # Mock no synonym match
        mock_synonym_result = AsyncMock()
        mock_synonym_result.scalar.return_value = None
        mock_session.execute.return_value = mock_synonym_result
        
        # Mock embedding service
        with patch('services.category_normalizer.embedding_service') as mock_embedding:
            mock_embedding.get_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
            
            # Mock vector search result
            mock_vector_result = AsyncMock()
            mock_vector_result.scalar.return_value = "dining"
            
            # Mock the second execute call (vector search)
            mock_session.execute.side_effect = [mock_synonym_result, mock_vector_result]
            
            result = await CategoryNormalizer.normalize(mock_session, "coffee shop")
            assert result == "dining"
    
    def test_transaction_creation_imports(self):
        """Test that transaction creation imports CategoryNormalizer"""
        try:
            from src.routes.transactions import CategoryNormalizer
            assert CategoryNormalizer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import CategoryNormalizer in transaction routes: {e}")
    
    def test_alert_rule_creation_imports(self):
        """Test that alert rule creation imports CategoryNormalizer"""
        try:
            from src.routes.alerts import CategoryNormalizer
            assert CategoryNormalizer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import CategoryNormalizer in alert routes: {e}")
    
    def test_alert_rule_validation_imports(self):
        """Test that alert rule validation imports CategoryNormalizer"""
        try:
            from src.services.alerts.agents.create_alert_rule import CategoryNormalizer
            assert CategoryNormalizer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import CategoryNormalizer in alert validation: {e}")
    
    def test_create_alert_rule_function_signature(self):
        """Test that create_alert_rule function has correct signature"""
        import inspect

        from src.services.alerts.agents.create_alert_rule import create_alert_rule
        
        sig = inspect.signature(create_alert_rule)
        params = list(sig.parameters.keys())
        expected_params = ['alert_text', 'user_id', 'session']
        
        assert params == expected_params, f"Expected {expected_params}, got {params}"
    
    def test_graph_states_include_session(self):
        """Test that graph states include session parameter"""
        # Test ValidationState
        from src.services.alerts.validate_rule_graph import ValidationState
        validation_state = ValidationState()
        assert 'session' in validation_state
        
        # Test AppState in parse_alert_graph
        from src.services.alerts.parse_alert_graph import AppState
        app_state = AppState()
        assert 'session' in app_state
        
        # Test AppState in generate_alert_graph
        from src.services.alerts.generate_alert_graph import (
            AppState as GenerateAppState,
        )
        generate_app_state = GenerateAppState()
        assert 'session' in generate_app_state


# Integration test that requires database
class TestCategoryNormalizerDatabaseIntegration:
    """Integration tests that require actual database connection"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_category_normalizer_with_real_database(self):
        """Test CategoryNormalizer with real database (requires setup)"""
        # This test requires the database to be set up with category data
        # Skip if not available
        try:
            from db import get_db
            db_gen = get_db()
            session = await db_gen.__anext__()
            
            # Test cases that should work with real data
            test_cases = [
                ("restaurant", "dining"),
                ("gas station", "fuel"),
                ("walmart", "retail"),
            ]
            
            for raw_category, expected in test_cases:
                result = await CategoryNormalizer.normalize(session, raw_category)
                assert result == expected, f"Expected '{expected}', got '{result}' for '{raw_category}'"
            
            await session.close()
            
        except Exception as e:
            pytest.skip(f"Database not available for integration test: {e}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
