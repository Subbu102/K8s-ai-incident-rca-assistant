"""
Vector store for storing and retrieving document embeddings.
"""

import logging
import json
import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class VectorStore:
    """In-memory vector store with similarity search."""
    
    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize vector store.
        
        Args:
            persist_path: Path to persist embeddings (optional)
        """
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = np.array([]).reshape(0, 0)
        self.persist_path = persist_path
        
        if persist_path and os.path.exists(persist_path):
            self._load()
    
    def add_document(self, text: str, embedding: np.ndarray, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a document to the store.
        
        Args:
            text: Document text
            embedding: Document embedding vector
            metadata: Optional metadata
        """
        doc = {
            "id": len(self.documents),
            "text": text,
            "metadata": metadata or {}
        }
        
        self.documents.append(doc)
        
        # Add embedding
        if self.embeddings.size == 0:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding.reshape(1, -1)])
        
        logger.debug(f"Added document {doc['id']}: {text[:100]}...")
    
    def add_documents(self, texts: List[str], embeddings: np.ndarray, metadata: Optional[List[Dict[str, Any]]] = None):
        """
        Add multiple documents to the store.
        
        Args:
            texts: List of document texts
            embeddings: Embeddings matrix (N x D)
            metadata: List of metadata dictionaries
        """
        if metadata is None:
            metadata = [{} for _ in texts]
        
        for text, embedding, meta in zip(texts, embeddings, metadata):
            self.add_document(text, embedding, meta)
        
        logger.info(f"Added {len(texts)} documents to vector store")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (text, similarity_score, metadata) tuples
        """
        if self.embeddings.size == 0:
            return []
        
        # Normalize embeddings
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        doc_norms = self.embeddings / (np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8)
        
        # Calculate similarities (cosine similarity)
        similarities = np.dot(doc_norms, query_norm)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = [
            (
                self.documents[idx]["text"],
                float(similarities[idx]),
                self.documents[idx]["metadata"]
            )
            for idx in top_indices
        ]
        
        return results
    
    def save(self):
        """Persist vector store to disk."""
        if not self.persist_path:
            logger.warning("No persist path set, skipping save")
            return
        
        try:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            
            data = {
                "documents": self.documents,
                "embeddings": self.embeddings.tolist()
            }
            
            with open(self.persist_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved vector store to {self.persist_path}")
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")
    
    def _load(self):
        """Load vector store from disk."""
        try:
            with open(self.persist_path, 'r') as f:
                data = json.load(f)
            
            self.documents = data.get("documents", [])
            self.embeddings = np.array(data.get("embeddings", []))
            
            logger.info(f"Loaded vector store from {self.persist_path}")
        except Exception as e:
            logger.error(f"Failed to load vector store: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "num_documents": len(self.documents),
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings.size > 0 else 0,
            "memory_usage_mb": self.embeddings.nbytes / (1024 * 1024) if self.embeddings.size > 0 else 0
        }
