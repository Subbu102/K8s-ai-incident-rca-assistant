"""
Embedding generation using HuggingFace models for RAG.
"""

import logging
import numpy as np
from typing import List, Union

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text documents."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers package required")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {model_name} (dim: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {str(e)}")
            raise
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Encode text(s) to embeddings.
        
        Args:
            texts: Single text or list of texts to encode
            
        Returns:
            Embedding vector(s) as numpy array
        """
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {str(e)}")
            raise
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a search query.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding
        """
        return self.encode(query)
    
    def encode_documents(self, documents: List[str]) -> np.ndarray:
        """
        Encode multiple documents.
        
        Args:
            documents: List of document texts
            
        Returns:
            Document embeddings matrix
        """
        return self.encode(documents)
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        try:
            embeddings = self.encode([text1, text2])
            
            # Cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {str(e)}")
            raise
