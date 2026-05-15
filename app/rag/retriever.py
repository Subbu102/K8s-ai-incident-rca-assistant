"""
RAG Retriever for fetching relevant context documents.
"""

import logging
from typing import List, Dict, Any, Optional

from .embedding import EmbeddingGenerator
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retrieval-Augmented Generation retriever."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", persist_path: Optional[str] = None):
        """
        Initialize RAG retriever.
        
        Args:
            model_name: HuggingFace embedding model name
            persist_path: Path to persist embeddings
        """
        try:
            self.embedding_generator = EmbeddingGenerator(model_name=model_name)
            self.vector_store = VectorStore(persist_path=persist_path)
            
            # Initialize with knowledge base documents
            self._initialize_knowledge_base()
            
            logger.info("RAG Retriever initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG retriever: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of document dicts with 'text' and optional 'metadata'
        """
        try:
            texts = [doc["text"] for doc in documents]
            embeddings = self.embedding_generator.encode_documents(texts)
            metadata = [doc.get("metadata", {}) for doc in documents]
            
            self.vector_store.add_documents(texts, embeddings, metadata)
            logger.info(f"Added {len(documents)} documents to knowledge base")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of relevant documents with scores
        """
        try:
            # Encode query
            query_embedding = self.embedding_generator.encode_query(query)
            
            # Search
            results = self.vector_store.search(query_embedding, k=k)
            
            # Format results
            formatted_results = [
                {
                    "text": text,
                    "score": float(score),
                    "metadata": metadata
                }
                for text, score, metadata in results
            ]
            
            logger.debug(f"Retrieved {len(formatted_results)} documents for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            raise
    
    def _initialize_knowledge_base(self):
        """Initialize with default Kubernetes troubleshooting knowledge base."""
        
        kb_documents = [
            {
                "text": "OOMKilled means the container was killed due to out-of-memory. Increase memory limits.",
                "metadata": {"category": "memory", "severity": "high"}
            },
            {
                "text": "CrashLoopBackOff indicates the pod keeps crashing. Check logs for errors.",
                "metadata": {"category": "pod", "severity": "high"}
            },
            {
                "text": "ImagePullBackOff means the container image cannot be pulled. Check image name and registry credentials.",
                "metadata": {"category": "image", "severity": "high"}
            },
            {
                "text": "Pending status often means insufficient resources. Check node capacity and resource requests.",
                "metadata": {"category": "resources", "severity": "medium"}
            },
            {
                "text": "Connection refused errors indicate the service is not running or listening. Verify service deployment.",
                "metadata": {"category": "networking", "severity": "high"}
            },
            {
                "text": "CPU throttling occurs when CPU limit is exceeded. Adjust resource limits or optimize code.",
                "metadata": {"category": "cpu", "severity": "medium"}
            },
            {
                "text": "Disk full errors require freeing space or increasing volume size.",
                "metadata": {"category": "storage", "severity": "high"}
            },
            {
                "text": "Permission denied errors often indicate wrong file permissions or RBAC policies.",
                "metadata": {"category": "security", "severity": "medium"}
            },
            {
                "text": "Timeout errors suggest network issues or service overload. Check network policies and service scaling.",
                "metadata": {"category": "networking", "severity": "medium"}
            },
            {
                "text": "Restart count high indicates application instability. Review logs and update deployment.",
                "metadata": {"category": "pod", "severity": "medium"}
            }
        ]
        
        if len(self.vector_store.documents) == 0:
            self.add_documents(kb_documents)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            "knowledge_base_size": len(self.vector_store.documents),
            "vector_store_stats": self.vector_store.get_stats()
        }
