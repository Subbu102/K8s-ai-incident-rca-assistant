"""
Quick start guide and examples.
"""

import asyncio
import json
from datetime import datetime

# Example 1: Create an incident programmatically
async def example_create_incident():
    """Example of creating an incident."""
    from app.api.incident_api import IncidentDetails
    
    incident = IncidentDetails(
        pod_name="app-deployment-5d4f8c9b7",
        namespace="production",
        error_message="Pod was terminated due to out-of-memory condition",
        severity="high",
        additional_context={
            "restart_count": 5,
            "memory_limit": "512Mi",
            "container_name": "app"
        }
    )
    
    print("Incident created:")
    print(json.dumps(incident.dict(), indent=2, default=str))


# Example 2: Initialize and test RCA engine
async def example_rca_analysis():
    """Example of RCA analysis."""
    from app.rag.retriever import RAGRetriever
    from app.llm.huggingface_client import HuggingFaceClient
    from app.rca.rca_engine import RCAEngine
    
    try:
        # Initialize components
        print("Initializing RCA Engine...")
        rag = RAGRetriever()
        llm = HuggingFaceClient()
        rca = RCAEngine(rag_retriever=rag, llm_client=llm)
        
        print("✓ RCA Engine initialized")
        
        # Analyze a hypothetical incident (without real K8s cluster)
        print("\nRCA Engine is ready for analysis")
        print("Example incident types it can analyze:")
        print("- OOMKilled (Out of Memory)")
        print("- CrashLoopBackOff (Container crashes)")
        print("- ImagePullBackOff (Image pull failures)")
        print("- Pending (Resource constraints)")
        print("- Connection errors (Network issues)")
        
    except Exception as e:
        print(f"Note: RCA analysis requires a Kubernetes cluster")
        print(f"Error: {str(e)}")


# Example 3: RAG retrieval
async def example_rag_retrieval():
    """Example of RAG knowledge retrieval."""
    from app.rag.retriever import RAGRetriever
    
    try:
        print("Initializing RAG Retriever...")
        retriever = RAGRetriever()
        
        # Query knowledge base
        query = "My pod is in OOMKilled status"
        results = retriever.retrieve(query, k=3)
        
        print(f"\nQuery: {query}")
        print(f"Results ({len(results)}):")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['text']}")
            print(f"   Score: {result['score']:.2%}")
        
        # Print stats
        stats = retriever.get_stats()
        print(f"\nKnowledge Base Stats:")
        print(f"- Documents: {stats['knowledge_base_size']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


# Example 4: Embedding generation
async def example_embeddings():
    """Example of text embedding."""
    from app.rag.embedding import EmbeddingGenerator
    
    try:
        print("Initializing Embedding Generator...")
        generator = EmbeddingGenerator()
        
        # Generate embeddings
        texts = [
            "The pod crashed with out of memory error",
            "Container failed to pull the image",
            "Service is not responding to requests"
        ]
        
        embeddings = generator.encode_documents(texts)
        
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Embedding dimension: {embeddings.shape[1]}")
        
        # Calculate similarity
        sim = generator.get_similarity(texts[0], texts[1])
        print(f"\nSimilarity between first two texts: {sim:.2%}")
        
    except Exception as e:
        print(f"Note: Embedding requires sentence-transformers")
        print(f"Error: {str(e)}")


async def main():
    """Run examples."""
    print("=" * 60)
    print("K8s AI Incident RCA Assistant - Quick Start Examples")
    print("=" * 60)
    
    print("\n[Example 1] Creating an Incident")
    print("-" * 60)
    await example_create_incident()
    
    print("\n[Example 2] RAG Knowledge Retrieval")
    print("-" * 60)
    await example_rag_retrieval()
    
    print("\n[Example 3] Text Embeddings")
    print("-" * 60)
    await example_embeddings()
    
    print("\n[Example 4] RCA Analysis Engine")
    print("-" * 60)
    await example_rca_analysis()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
