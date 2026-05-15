"""
Unit tests for the RAG retriever.
"""

import pytest
from app.rag.retriever import RAGRetriever
from app.rag.embedding import EmbeddingGenerator


class TestRAGRetriever:
    """Test cases for RAG retriever."""
    
    @pytest.mark.asyncio
    async def test_retriever_initialization(self):
        """Test RAG retriever can be initialized."""
        retriever = RAGRetriever()
        assert retriever is not None
        assert len(retriever.vector_store.documents) > 0
    
    @pytest.mark.asyncio
    async def test_knowledge_base_loaded(self):
        """Test knowledge base is loaded."""
        retriever = RAGRetriever()
        stats = retriever.get_stats()
        assert stats["knowledge_base_size"] > 0
    
    @pytest.mark.asyncio
    async def test_document_retrieval(self):
        """Test document retrieval."""
        retriever = RAGRetriever()
        
        query = "OOMKilled pod issue"
        results = retriever.retrieve(query, k=3)
        
        assert len(results) > 0
        assert all("text" in r for r in results)
        assert all("score" in r for r in results)
        assert all(0 <= r["score"] <= 1 for r in results)
    
    @pytest.mark.asyncio
    async def test_add_documents(self):
        """Test adding documents to knowledge base."""
        retriever = RAGRetriever()
        initial_count = len(retriever.vector_store.documents)
        
        new_docs = [
            {"text": "Test document 1", "metadata": {"type": "test"}},
            {"text": "Test document 2", "metadata": {"type": "test"}}
        ]
        
        retriever.add_documents(new_docs)
        
        assert len(retriever.vector_store.documents) == initial_count + 2


class TestEmbeddingGenerator:
    """Test cases for embedding generator."""
    
    @pytest.mark.asyncio
    async def test_embedding_generation(self):
        """Test embedding generation."""
        try:
            generator = EmbeddingGenerator()
            embedding = generator.encode("Test text")
            
            assert embedding.shape[0] == 1
            assert embedding.shape[1] > 0
        except ImportError:
            pytest.skip("sentence-transformers not installed")
    
    @pytest.mark.asyncio
    async def test_multiple_embeddings(self):
        """Test generating multiple embeddings."""
        try:
            generator = EmbeddingGenerator()
            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = generator.encode_documents(texts)
            
            assert embeddings.shape[0] == 3
            assert embeddings.shape[1] > 0
        except ImportError:
            pytest.skip("sentence-transformers not installed")
    
    @pytest.mark.asyncio
    async def test_similarity_calculation(self):
        """Test similarity calculation."""
        try:
            generator = EmbeddingGenerator()
            
            text1 = "The pod crashed"
            text2 = "Container exited abnormally"
            
            similarity = generator.get_similarity(text1, text2)
            
            assert 0 <= similarity <= 1
        except ImportError:
            pytest.skip("sentence-transformers not installed")
