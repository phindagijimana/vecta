"""
RAG System using ChromaDB for Vecta AI
Phase 3 Implementation: Week 5-8

Features:
- Vector database for clinical guidelines
- Semantic search for relevant context
- Dynamic retrieval for prompts
- Support for ILAE, ICHD-3, AAN guidelines
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger("vectaai.rag")

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
    logger.info("✅ ChromaDB and sentence-transformers available")
except ImportError as e:
    CHROMA_AVAILABLE = False
    logger.warning(f"⚠️ ChromaDB or sentence-transformers not available: {e}")
    logger.warning("   Install with: pip install chromadb sentence-transformers")


class VectaAIRAGSystem:
    """
    Retrieval-Augmented Generation (RAG) System for Vecta AI
    
    Uses ChromaDB for vector storage and retrieval of clinical guidelines.
    """
    
    def __init__(self, data_dir: str = None, persist_dir: str = None):
        """
        Initialize RAG system
        
        Args:
            data_dir: Directory containing guidelines JSON files
            persist_dir: Directory to persist ChromaDB database
        """
        if not CHROMA_AVAILABLE:
            self.available = False
            logger.warning("RAG system not available - missing dependencies")
            return
        
        self.available = True
        
        # Set paths
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        if persist_dir is None:
            persist_dir = os.path.join(data_dir, "vector_db")
        
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model (free, open-source)
        logger.info("Loading embedding model (sentence-transformers)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Embedding model loaded")
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at {self.persist_dir}...")
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Get or create collection
        self.collection_name = "clinical_guidelines"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"✅ Loaded existing collection '{self.collection_name}'")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Vecta AI Clinical Guidelines"}
            )
            logger.info(f"✅ Created new collection '{self.collection_name}'")
            # Index guidelines on first run
            self._index_guidelines()
    
    def _load_guidelines(self) -> Dict:
        """Load guidelines from JSON file"""
        guidelines_path = self.data_dir / "guidelines" / "neurology_guidelines.json"
        
        if not guidelines_path.exists():
            logger.warning(f"Guidelines file not found: {guidelines_path}")
            return {}
        
        with open(guidelines_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"✅ Loaded guidelines from {guidelines_path}")
        return data.get("neurology_guidelines", {})
    
    def _flatten_guidelines(self, guidelines: Dict) -> List[Dict]:
        """
        Flatten nested guidelines structure into chunks for indexing
        
        Returns list of dicts with: {id, condition, topic, content, source, url}
        """
        chunks = []
        chunk_id = 0
        
        for condition, topics in guidelines.items():
            if not isinstance(topics, dict):
                continue
            
            for topic, data in topics.items():
                if not isinstance(data, dict):
                    continue
                
                content = data.get("content", "")
                source = data.get("source", "")
                url = data.get("url", "")
                
                # If content is a dict, convert to text
                if isinstance(content, dict):
                    content = self._dict_to_text(content)
                elif isinstance(content, list):
                    content = "\n".join(str(item) for item in content)
                
                if content and isinstance(content, str):
                    chunks.append({
                        "id": f"guideline_{chunk_id}",
                        "condition": condition,
                        "topic": topic,
                        "content": content,
                        "source": source,
                        "url": url
                    })
                    chunk_id += 1
        
        logger.info(f"✅ Flattened guidelines into {len(chunks)} chunks")
        return chunks
    
    def _dict_to_text(self, d: Dict) -> str:
        """Convert nested dict to readable text"""
        lines = []
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                lines.append(self._dict_to_text(value))
            elif isinstance(value, list):
                lines.append(f"{key}:")
                lines.extend(f"  - {item}" for item in value)
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _index_guidelines(self):
        """Index all clinical guidelines into ChromaDB"""
        logger.info("Indexing clinical guidelines...")
        
        # Load and flatten guidelines
        guidelines = self._load_guidelines()
        if not guidelines:
            logger.warning("No guidelines found to index")
            return
        
        chunks = self._flatten_guidelines(guidelines)
        if not chunks:
            logger.warning("No guideline chunks to index")
            return
        
        # Prepare data for ChromaDB
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [
            {
                "condition": chunk["condition"],
                "topic": chunk["topic"],
                "source": chunk["source"],
                "url": chunk["url"]
            }
            for chunk in chunks
        ]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} chunks...")
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
        embeddings = embeddings.tolist()
        
        # Add to ChromaDB
        logger.info("Adding to ChromaDB...")
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        logger.info(f"✅ Indexed {len(chunks)} guideline chunks into ChromaDB")
    
    def retrieve(self, query: str, condition: Optional[str] = None, n_results: int = 3) -> str:
        """
        Retrieve relevant guideline chunks for a query
        
        Args:
            query: Query text (e.g., patient case description)
            condition: Optional condition filter (epilepsy, stroke, etc.)
            n_results: Number of results to retrieve
        
        Returns:
            Formatted string with retrieved guidelines
        """
        if not self.available:
            return ""
        
        try:
            # Build filter
            where_filter = None
            if condition:
                where_filter = {"condition": condition}
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            if not results or not results['documents'] or not results['documents'][0]:
                return ""
            
            formatted_parts = []
            formatted_parts.append("📚 RELEVANT CLINICAL GUIDELINES (RAG):\n")
            
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                formatted_parts.append(f"\n{i}. {metadata.get('topic', 'Guideline').upper()}:")
                formatted_parts.append(f"   Source: {metadata.get('source', 'N/A')}")
                formatted_parts.append(f"   {doc}\n")
            
            return "\n".join(formatted_parts)
        
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return ""
    
    def get_stats(self) -> Dict:
        """Get statistics about the RAG system"""
        if not self.available:
            return {"available": False}
        
        try:
            count = self.collection.count()
            return {
                "available": True,
                "collection_name": self.collection_name,
                "total_chunks": count,
                "embedding_model": "all-MiniLM-L6-v2",
                "persist_dir": str(self.persist_dir)
            }
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {"available": True, "error": str(e)}


# Global RAG instance (initialized on first import)
_rag_system = None

def get_rag_system() -> Optional[VectaAIRAGSystem]:
    """Get or initialize the global RAG system"""
    global _rag_system
    
    if _rag_system is None:
        try:
            _rag_system = VectaAIRAGSystem()
            logger.info("✅ RAG system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            _rag_system = None
    
    return _rag_system


if __name__ == "__main__":
    # Test RAG system
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("Testing Vecta AI RAG System")
    print("="*70 + "\n")
    
    # Initialize
    rag = VectaAIRAGSystem()
    
    # Get stats
    stats = rag.get_stats()
    print("\n📊 RAG System Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test retrieval
    print("\n🔍 Testing Retrieval:\n")
    
    test_queries = [
        ("Patient with absence seizures and 3Hz spike-wave on EEG", "epilepsy"),
        ("Tremor and bradykinesia, responds to levodopa", "parkinsons"),
        ("Acute onset hemiparesis, MRI shows ischemic stroke", "stroke")
    ]
    
    for query, condition in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"Condition: {condition}")
        print(f"{'='*70}")
        
        results = rag.retrieve(query, condition=condition, n_results=2)
        print(results)
    
    print("\n" + "="*70)
    print("✅ RAG System Test Complete")
    print("="*70 + "\n")
