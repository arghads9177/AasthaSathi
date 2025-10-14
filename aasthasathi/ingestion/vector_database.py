"""
Vector Database Setup and Management

Handles ChromaDB initialization, embeddings generation,
and document indexing for the RAG system.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Tuple
import logging
import numpy as np
from pathlib import Path
import hashlib
import json
from datetime import datetime

from ..core.config import get_settings
from ..core.models import Document, DocumentChunk, DocumentSource


logger = logging.getLogger(__name__)


class VectorDatabase:
    """Manages ChromaDB for document storage and retrieval."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize ChromaDB client and collection."""
        
        # Create vector database directory
        db_path = Path(self.settings.vector_db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.settings.chroma_collection_name
            )
            logger.info(f"Connected to existing collection: {self.settings.chroma_collection_name}")
        except ValueError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=self.settings.chroma_collection_name,
                metadata={"description": "AasthaSathi knowledge base"}
            )
            logger.info(f"Created new collection: {self.settings.chroma_collection_name}")
        
        # Initialize embedding model
        try:
            from ..llm.embeddings import get_embedding_model
            self.embedding_model = get_embedding_model()
            logger.info(f"Initialized embedding model: {self.settings.embedding_provider}")
        except Exception as e:
            logger.warning(f"Could not initialize embedding model: {e}")
            self.embedding_model = None
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector database."""
        
        try:
            logger.info(f"Adding {len(documents)} documents to vector database")
            
            # Prepare data for ChromaDB
            ids = []
            documents_text = []
            metadatas = []
            
            for doc in documents:
                ids.append(doc.doc_id)
                documents_text.append(doc.content)
                
                # Prepare metadata (ChromaDB only accepts certain types)
                metadata = {
                    "title": doc.title,
                    "source": doc.source.value,
                    "doc_id": doc.doc_id,
                    "content_length": len(doc.content),
                    "word_count": len(doc.content.split())
                }
                
                # Add optional fields
                if doc.url:
                    metadata["url"] = doc.url
                if doc.page_number:
                    metadata["page_number"] = doc.page_number
                if doc.section:
                    metadata["section"] = doc.section
                
                # Add custom metadata
                for key, value in doc.metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    else:
                        # Convert complex types to string
                        metadata[key] = str(value)
                
                metadatas.append(metadata)
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents_text,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector database: {e}")
            return False
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the vector database."""
        
        try:
            logger.info(f"Adding {len(chunks)} chunks to vector database")
            
            # Prepare data for ChromaDB
            ids = []
            documents_text = []
            metadatas = []
            
            for chunk in chunks:
                ids.append(chunk.chunk_id)
                documents_text.append(chunk.content)
                
                # Prepare metadata
                metadata = {
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "chunk_index": chunk.chunk_index,
                    "content_length": len(chunk.content),
                    "word_count": len(chunk.content.split())
                }
                
                # Add chunk metadata
                for key, value in chunk.metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    else:
                        metadata[key] = str(value)
                
                metadatas.append(metadata)
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents_text,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector database: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5, 
                        source_filter: Optional[str] = None,
                        metadata_filter: Optional[Dict] = None) -> List[Dict]:
        """Search for similar documents."""
        
        try:
            # Prepare where clause for filtering
            where_clause = {}
            
            if source_filter:
                where_clause["source"] = source_filter
            
            if metadata_filter:
                where_clause.update(metadata_filter)
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'metadata': results['metadatas'][0][i]
                    }
                    formatted_results.append(result)
            
            logger.debug(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        
        try:
            count = self.collection.count()
            
            # Get sample metadata to understand data distribution
            sample_results = self.collection.get(limit=100)
            
            sources = {}
            if sample_results['metadatas']:
                for metadata in sample_results['metadatas']:
                    source = metadata.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
            
            stats = {
                'total_documents': count,
                'collection_name': self.settings.chroma_collection_name,
                'source_distribution': sources,
                'embedding_model': self.settings.embedding_model,
                'database_path': self.settings.vector_db_path
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """Delete documents by IDs."""
        
        try:
            self.collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        
        try:
            # Delete and recreate collection
            self.client.delete_collection(self.settings.chroma_collection_name)
            self.collection = self.client.create_collection(
                name=self.settings.chroma_collection_name,
                metadata={"description": "AasthaSathi knowledge base"}
            )
            logger.info("Cleared all documents from collection")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def backup_collection(self, backup_path: str) -> bool:
        """Backup collection data."""
        
        try:
            backup_path = Path(backup_path)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Get all documents
            results = self.collection.get()
            
            # Save to JSON
            backup_data = {
                'collection_name': self.settings.chroma_collection_name,
                'total_documents': len(results['ids']),
                'ids': results['ids'],
                'documents': results['documents'],
                'metadatas': results['metadatas'],
                'backup_timestamp': str(datetime.now().isoformat())
            }
            
            backup_file = backup_path / f"chroma_backup_{self.settings.chroma_collection_name}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Backed up collection to {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up collection: {e}")
            return False


class DocumentIndexer:
    """Handles the complete document indexing pipeline."""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.settings = get_settings()
    
    def index_documents(self, documents: List[Document], 
                       use_chunking: bool = True) -> bool:
        """Index documents in the vector database."""
        
        logger.info(f"Starting indexing for {len(documents)} documents")
        
        try:
            if use_chunking:
                # Create chunks from documents
                from .pdf_processor import PDFProcessor
                
                processor = PDFProcessor()
                chunks = processor.create_chunks(documents)
                
                # Add chunks to vector database
                success = self.vector_db.add_chunks(chunks)
                
                if success:
                    logger.info(f"Successfully indexed {len(chunks)} chunks from {len(documents)} documents")
                
            else:
                # Add documents directly
                success = self.vector_db.add_documents(documents)
                
                if success:
                    logger.info(f"Successfully indexed {len(documents)} documents")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during document indexing: {e}")
            return False
    
    def reindex_collection(self, documents: List[Document]) -> bool:
        """Clear collection and reindex all documents."""
        
        logger.info("Starting collection reindexing")
        
        # Clear existing collection
        if not self.vector_db.clear_collection():
            return False
        
        # Index new documents
        return self.index_documents(documents)


def create_vector_database() -> VectorDatabase:
    """Factory function to create vector database instance."""
    return VectorDatabase()


def index_documents_from_sources(website_docs: List[Document] = None,
                                pdf_docs: List[Document] = None) -> bool:
    """Index documents from multiple sources."""
    
    indexer = DocumentIndexer()
    all_documents = []
    
    if website_docs:
        all_documents.extend(website_docs)
        logger.info(f"Added {len(website_docs)} website documents")
    
    if pdf_docs:
        all_documents.extend(pdf_docs)
        logger.info(f"Added {len(pdf_docs)} PDF documents")
    
    if all_documents:
        return indexer.index_documents(all_documents)
    else:
        logger.warning("No documents provided for indexing")
        return False


if __name__ == "__main__":
    # Test the vector database
    
    # Create test documents
    test_docs = [
        Document(
            doc_id="test_1",
            title="Fixed Deposit Scheme",
            content="Our Fixed Deposit scheme offers attractive interest rates with flexible tenure options. Minimum deposit amount is Rs. 1000 with a maximum of Rs. 10 lakh.",
            source=DocumentSource.WEBSITE,
            url="http://myaastha.in/fd-scheme"
        ),
        Document(
            doc_id="test_2", 
            title="Loan Policy",
            content="Personal loans are available for salaried individuals with minimum income of Rs. 25,000 per month. Interest rate starts from 12% per annum.",
            source=DocumentSource.PDF_MANUAL,
            page_number=5
        )
    ]
    
    # Initialize and test
    vector_db = VectorDatabase()
    
    # Add documents
    success = vector_db.add_documents(test_docs)
    print(f"Added documents: {success}")
    
    # Search
    results = vector_db.search_documents("fixed deposit interest rate", n_results=2)
    print(f"\nSearch results: {len(results)}")
    
    for result in results:
        print(f"- {result['metadata']['title']}: {result['similarity']:.3f}")
        print(f"  Content: {result['content'][:100]}...")
    
    # Stats
    stats = vector_db.get_collection_stats()
    print(f"\nCollection stats: {stats}")