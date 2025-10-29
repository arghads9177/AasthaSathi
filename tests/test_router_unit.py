"""
Unit tests for the Query Router.

Run with: pytest tests/test_router_unit.py -v
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.router import QueryRouter, RouteQuery, route_query


class TestQueryRouter:
    """Unit tests for QueryRouter class."""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing."""
        return QueryRouter()
    
    def test_router_initialization(self, router):
        """Test that router initializes correctly."""
        assert router is not None
        assert router.llm is not None
        assert router.chain is not None
        assert router.temperature == 0
    
    def test_router_with_custom_model(self):
        """Test router initialization with custom model."""
        router = QueryRouter(model_name="gpt-4", temperature=0.5)
        assert router.model_name == "gpt-4"
        assert router.temperature == 0.5
    
    def test_route_returns_route_query(self, router):
        """Test that route returns a RouteQuery object."""
        query = "Where are branches in Kolkata?"
        result = router.route(query)
        assert isinstance(result, RouteQuery)
        assert hasattr(result, 'datasource')
        assert hasattr(result, 'reasoning')
        assert hasattr(result, 'api_queries')
    
    def test_route_dict_returns_dict(self, router):
        """Test that route_dict returns a dictionary."""
        query = "What are the current FD rates?"
        result = router.route_dict(query)
        assert isinstance(result, dict)
        assert 'datasource' in result
        assert 'reasoning' in result
        assert 'api_queries' in result
    
    def test_api_routing(self, router):
        """Test that API queries are routed correctly."""
        api_queries = [
            "Where are branches in Delhi?",
            "What are the current loan schemes?",
            "Show me FD interest rates",
            "List all active branches",
        ]
        
        for query in api_queries:
            result = router.route(query)
            assert result.datasource == "api", f"Failed for query: {query}"
            assert len(result.reasoning) > 0
    
    def test_rag_routing(self, router):
        """Test that RAG queries are routed correctly."""
        rag_queries = [
            "How do I open a savings account?",
            "What is the difference between FD and RD?",
            "Explain KYC requirements",
            "What documents are needed for a loan?",
        ]
        
        for query in rag_queries:
            result = router.route(query)
            assert result.datasource == "rag", f"Failed for query: {query}"
            assert len(result.reasoning) > 0
    
    def test_hybrid_routing(self, router):
        """Test that hybrid queries are routed correctly."""
        hybrid_queries = [
            "Tell me about FD schemes and show current rates",
            "What branches are in Mumbai and how do I open account?",
            "Explain loan options and show available schemes",
        ]
        
        for query in hybrid_queries:
            result = router.route(query)
            assert result.datasource == "hybrid", f"Failed for query: {query}"
            assert len(result.reasoning) > 0
            assert len(result.api_queries) > 0
    
    def test_api_queries_field(self, router):
        """Test that api_queries field is populated for API and hybrid routes."""
        # API route should have api_queries
        api_result = router.route("Show me branches in Kolkata")
        assert api_result.datasource == "api"
        assert len(api_result.api_queries) > 0
        
        # Hybrid route should have api_queries
        hybrid_result = router.route("Tell me about FD and show current rates")
        assert hybrid_result.datasource == "hybrid"
        assert len(hybrid_result.api_queries) > 0
        
        # RAG route may or may not have api_queries (usually empty)
        rag_result = router.route("How do I open an account?")
        assert rag_result.datasource == "rag"
    
    def test_convenience_function(self):
        """Test the convenience route_query function."""
        result = route_query("Where are branches in Delhi?")
        assert isinstance(result, RouteQuery)
        assert result.datasource == "api"
    
    def test_empty_query(self, router):
        """Test router behavior with empty query."""
        result = router.route("")
        assert result.datasource in ["api", "rag", "hybrid"]
        assert len(result.reasoning) > 0
    
    def test_ambiguous_query(self, router):
        """Test router behavior with ambiguous queries."""
        ambiguous_queries = [
            "Account",
            "Branch",
            "Loan",
        ]
        
        for query in ambiguous_queries:
            result = router.route(query)
            assert result.datasource in ["api", "rag", "hybrid"]
            assert len(result.reasoning) > 0


class TestRouteQuery:
    """Unit tests for RouteQuery model."""
    
    def test_route_query_creation(self):
        """Test RouteQuery model creation."""
        route = RouteQuery(
            datasource="api",
            reasoning="Test reasoning",
            api_queries=["test query"]
        )
        assert route.datasource == "api"
        assert route.reasoning == "Test reasoning"
        assert route.api_queries == ["test query"]
    
    def test_route_query_default_api_queries(self):
        """Test RouteQuery with default api_queries."""
        route = RouteQuery(
            datasource="rag",
            reasoning="Test reasoning"
        )
        assert route.api_queries == []
    
    def test_route_query_valid_datasources(self):
        """Test that only valid datasources are accepted."""
        valid_sources = ["api", "rag", "hybrid"]
        
        for source in valid_sources:
            route = RouteQuery(
                datasource=source,
                reasoning="Test"
            )
            assert route.datasource == source


class TestRouterIntegration:
    """Integration tests for router with different scenarios."""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing."""
        return QueryRouter()
    
    def test_branch_queries(self, router):
        """Test various branch-related queries."""
        test_cases = [
            ("Where is the nearest branch?", "api"),
            ("What is a bank branch?", "rag"),
            ("Show branches in Kolkata and explain their services", "hybrid"),
        ]
        
        for query, expected in test_cases:
            result = router.route(query)
            assert result.datasource == expected, f"Failed for: {query}"
    
    def test_deposit_queries(self, router):
        """Test various deposit-related queries."""
        test_cases = [
            ("What are the FD rates?", "api"),
            ("How does fixed deposit work?", "rag"),
            ("Explain FD and show me the rates", "hybrid"),
        ]
        
        for query, expected in test_cases:
            result = router.route(query)
            assert result.datasource == expected, f"Failed for: {query}"
    
    def test_loan_queries(self, router):
        """Test various loan-related queries."""
        test_cases = [
            ("What loan schemes are available?", "api"),
            ("What documents do I need for a loan?", "rag"),
            ("Tell me about loans and show current schemes", "hybrid"),
        ]
        
        for query, expected in test_cases:
            result = router.route(query)
            assert result.datasource == expected, f"Failed for: {query}"
    
    def test_consistency(self, router):
        """Test that router returns consistent results for same query."""
        query = "Where are branches in Delhi?"
        
        results = [router.route(query) for _ in range(3)]
        datasources = [r.datasource for r in results]
        
        # All results should be the same (temperature=0)
        assert len(set(datasources)) == 1, "Router returned inconsistent results"


# Pytest markers for different test categories
pytestmark = [
    pytest.mark.unit,
]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
