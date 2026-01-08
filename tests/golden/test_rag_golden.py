"""
Golden Tests for RAG Retrieval
Tests that RAG retrieves expected documents for specific queries
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag import RAGEngine


def is_kb_built():
    """Check if knowledge base is built"""
    kb_path = Path(".kb")
    return kb_path.exists() and (kb_path / "index.json").exists()


@pytest.mark.skipif(not is_kb_built(), reason="Knowledge base not built. Run 'twx-agent rag build' first.")
class TestRAGGolden:
    """
    Golden tests for RAG retrieval
    These tests verify that RAG retrieves the expected documentation
    """
    
    def test_service_creation_query(self):
        """Test that service creation query retrieves ServiceHelper docs"""
        engine = RAGEngine()
        
        query = "How do I create a service in ThingWorx?"
        results = engine.query(query, top_k=5)
        
        assert len(results) > 0, "No results returned"
        
        # Check that relevant files are in top results
        files = [r["file"] for r in results]
        
        # Should retrieve ServiceHelper or LLM_INSTRUCTIONS
        relevant_files = [
            "docs/AddServiceToThing_Code.js",
            "docs/LLM_INSTRUCTIONS.md",
            "docs/Advanced_Service_Management.md"
        ]
        
        found = any(any(rf in f for rf in relevant_files) for f in files)
        assert found, f"Expected files not found in results. Got: {files}"
    
    def test_service_helper_query(self):
        """Test that ServiceHelper query retrieves correct documentation"""
        engine = RAGEngine()
        
        query = "ServiceHelper AddServiceToThing usage"
        results = engine.query(query, top_k=5)
        
        assert len(results) > 0, "No results returned"
        
        # Top result should be ServiceHelper related
        top_file = results[0]["file"]
        
        assert "ServiceHelper" in top_file or "AddServiceToThing" in top_file, \
            f"Top result not ServiceHelper related: {top_file}"
    
    def test_api_guide_query(self):
        """Test that API query retrieves API guide"""
        engine = RAGEngine()
        
        query = "ThingWorx REST API endpoints for creating Things"
        results = engine.query(query, top_k=5)
        
        assert len(results) > 0, "No results returned"
        
        # Should retrieve API guide
        files = [r["file"] for r in results]
        
        found = any("API_Guide" in f or "ThingWorx_API" in f for f in files)
        assert found, f"API guide not found in results. Got: {files}"
    
    def test_credentials_query(self):
        """Test that credentials query retrieves credentials management docs"""
        engine = RAGEngine()
        
        query = "How to manage credentials and AppKey?"
        results = engine.query(query, top_k=5)
        
        assert len(results) > 0, "No results returned"
        
        # Should retrieve credentials docs
        files = [r["file"] for r in results]
        
        found = any("Credentials" in f or "Managing_Credentials" in f for f in files)
        assert found, f"Credentials docs not found in results. Got: {files}"
    
    def test_service_header_query(self):
        """Test that service header query retrieves header standard"""
        engine = RAGEngine()
        
        query = "Service header format and change log"
        results = engine.query(query, top_k=5)
        
        assert len(results) > 0, "No results returned"
        
        # Should retrieve service header standard
        files = [r["file"] for r in results]
        
        found = any("Service_Header" in f or "LLM_INSTRUCTIONS" in f for f in files)
        assert found, f"Service header docs not found in results. Got: {files}"
    
    def test_relevance_scores(self):
        """Test that relevance scores are reasonable"""
        engine = RAGEngine()
        
        query = "How to use ServiceHelper?"
        results = engine.query(query, top_k=5)
        
        assert len(results) > 0, "No results returned"
        
        # Top result should have high relevance
        top_relevance = results[0]["relevance"]
        assert top_relevance > 0.5, f"Top relevance too low: {top_relevance}"
        
        # Relevance should be sorted descending
        relevances = [r["relevance"] for r in results]
        assert relevances == sorted(relevances, reverse=True), \
            "Results not sorted by relevance"
    
    def test_context_generation(self):
        """Test that context generation works properly"""
        engine = RAGEngine()
        
        query = "Create a service with ServiceHelper"
        context, sources = engine.get_context(query, max_tokens=1000)
        
        assert context, "Context is empty"
        assert sources, "Sources list is empty"
        
        # Context should contain relevant information
        assert "ServiceHelper" in context or "AddServiceToThing" in context, \
            "Context doesn't contain relevant keywords"
        
        # Sources should have required fields
        for source in sources:
            assert "file" in source
            assert "section" in source
            assert "relevance" in source
            assert 0 <= source["relevance"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
