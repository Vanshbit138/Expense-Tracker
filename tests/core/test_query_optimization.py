"""
Tests for query optimization module.
"""

from unittest.mock import MagicMock

from src.core.query_optimization import (
    AsyncQueryOptimizer,
    IndexOptimizer,
    QueryAnalyzer,
    QueryOptimizer,
)


class TestQueryOptimizer:
    """Test cases for QueryOptimizer."""

    def test_query_optimizer_class_exists(self):
        """Test that QueryOptimizer class exists."""
        assert QueryOptimizer is not None

    def test_add_pagination_static_method(self):
        """Test add_pagination static method exists."""
        assert hasattr(QueryOptimizer, "add_pagination")
        assert callable(QueryOptimizer.add_pagination)

    def test_add_ordering_static_method(self):
        """Test add_ordering static method exists."""
        assert hasattr(QueryOptimizer, "add_ordering")
        assert callable(QueryOptimizer.add_ordering)

    def test_add_filters_static_method(self):
        """Test add_filters static method exists."""
        assert hasattr(QueryOptimizer, "add_filters")
        assert callable(QueryOptimizer.add_filters)

    def test_add_relations_static_method(self):
        """Test add_relations static method exists."""
        assert hasattr(QueryOptimizer, "add_relations")
        assert callable(QueryOptimizer.add_relations)

    def test_add_selectin_relations_static_method(self):
        """Test add_selectin_relations static method exists."""
        assert hasattr(QueryOptimizer, "add_selectin_relations")
        assert callable(QueryOptimizer.add_selectin_relations)


class TestIndexOptimizer:
    """Test cases for IndexOptimizer."""

    def test_index_optimizer_class_exists(self):
        """Test that IndexOptimizer class exists."""
        assert IndexOptimizer is not None

    def test_get_recommended_indexes_static_method(self):
        """Test get_recommended_indexes static method exists."""
        assert hasattr(IndexOptimizer, "get_recommended_indexes")
        assert callable(IndexOptimizer.get_recommended_indexes)

    def test_create_recommended_indexes_static_method(self):
        """Test create_recommended_indexes static method exists."""
        assert hasattr(IndexOptimizer, "create_recommended_indexes")
        assert callable(IndexOptimizer.create_recommended_indexes)

    def test_get_recommended_indexes_returns_list(self):
        """Test get_recommended_indexes returns a list."""
        indexes = IndexOptimizer.get_recommended_indexes()
        assert isinstance(indexes, list)
        assert len(indexes) > 0


class TestAsyncQueryOptimizer:
    """Test cases for AsyncQueryOptimizer."""

    def test_async_query_optimizer_class_exists(self):
        """Test that AsyncQueryOptimizer class exists."""
        assert AsyncQueryOptimizer is not None

    def test_execute_optimized_query_static_method(self):
        """Test execute_optimized_query static method exists."""
        assert hasattr(AsyncQueryOptimizer, "execute_optimized_query")
        assert callable(AsyncQueryOptimizer.execute_optimized_query)

    def test_get_count_optimized_static_method(self):
        """Test get_count_optimized static method exists."""
        assert hasattr(AsyncQueryOptimizer, "get_count_optimized")
        assert callable(AsyncQueryOptimizer.get_count_optimized)

    def test_get_paginated_results_static_method(self):
        """Test get_paginated_results static method exists."""
        assert hasattr(AsyncQueryOptimizer, "get_paginated_results")
        assert callable(AsyncQueryOptimizer.get_paginated_results)


class TestQueryAnalyzer:
    """Test cases for QueryAnalyzer."""

    def test_query_analyzer_class_exists(self):
        """Test that QueryAnalyzer class exists."""
        assert QueryAnalyzer is not None

    def test_analyze_query_performance_static_method(self):
        """Test analyze_query_performance static method exists."""
        assert hasattr(QueryAnalyzer, "analyze_query_performance")
        assert callable(QueryAnalyzer.analyze_query_performance)

    def test_get_query_explanation_static_method(self):
        """Test get_query_explanation static method exists."""
        assert hasattr(QueryAnalyzer, "get_query_explanation")
        assert callable(QueryAnalyzer.get_query_explanation)

    def test_analyze_query_performance_returns_dict(self):
        """Test analyze_query_performance returns a dictionary."""
        mock_query = MagicMock()
        # Fix: Properly mock the __str__ method to handle self parameter
        mock_query.__str__ = MagicMock(return_value="SELECT * FROM users")

        result = QueryAnalyzer.analyze_query_performance(mock_query)
        assert isinstance(result, dict)
        assert "query" in result
        assert "suggestions" in result
        assert "warnings" in result

    def test_analyze_query_performance_with_where_clause(self):
        """Test analyze_query_performance with WHERE clause."""
        mock_query = MagicMock()
        mock_query.__str__ = MagicMock(return_value="SELECT * FROM users WHERE id = 1")

        result = QueryAnalyzer.analyze_query_performance(mock_query)
        assert isinstance(result, dict)
        assert "query" in result
        assert "suggestions" in result
        assert "warnings" in result
        # Should suggest adding indexes for WHERE clause
        assert any(
            "index" in suggestion.lower() for suggestion in result["suggestions"]
        )

    def test_analyze_query_performance_with_order_by(self):
        """Test analyze_query_performance with ORDER BY clause."""
        mock_query = MagicMock()
        mock_query.__str__ = MagicMock(return_value="SELECT * FROM users ORDER BY name")

        result = QueryAnalyzer.analyze_query_performance(mock_query)
        assert isinstance(result, dict)
        assert "query" in result
        assert "suggestions" in result
        assert "warnings" in result
        # Should warn about ORDER BY without LIMIT
        assert any("order by" in warning.lower() for warning in result["warnings"])

    def test_analyze_query_performance_with_select_star(self):
        """Test analyze_query_performance with SELECT *."""
        mock_query = MagicMock()
        mock_query.__str__ = MagicMock(return_value="SELECT * FROM users")

        result = QueryAnalyzer.analyze_query_performance(mock_query)
        assert isinstance(result, dict)
        assert "query" in result
        assert "suggestions" in result
        assert "warnings" in result
        # Should suggest avoiding SELECT *
        assert any(
            "select" in suggestion.lower() for suggestion in result["suggestions"]
        )

    def test_get_query_explanation_returns_string(self):
        """Test get_query_explanation returns a string."""
        mock_query = MagicMock()
        mock_query.__str__ = MagicMock(return_value="SELECT * FROM users")
        mock_query.compile = MagicMock(return_value="SELECT * FROM users")

        result = QueryAnalyzer.get_query_explanation(mock_query)
        assert isinstance(result, str)
        assert "Query:" in result
        assert "Compiled:" in result
