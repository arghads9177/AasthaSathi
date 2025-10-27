"""
Vector Store Manager for ChromaDB Operations

Handles all ChromaDB operations including initialization, document storage,
retrieval, and collection management.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging
import json
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from langchain.schema import Document

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manager for ChromaDB vector store operations."""
    
    def __init__(self, collection_name: Optional[str] = None, persist_directory: Optional[str] = None):
        """
        Initialize the Vector Store Manager.
        
        Args:
            collection_name: Name of the ChromaDB collection. If None, uses config default
            persist_directory: Path to persist ChromaDB data. If None, uses config default
        """
        self.settings = get_settings()
        
        # Set collection name
        self.collection_name = collection_name or self.settings.chroma_collection_name
        
        # Set persist directory
        if persist_directory:
            self.persist_directory = Path(persist_directory)
        else:
            self.persist_directory = Path(self.settings.vector_db_path)
        
        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.collection = None
        
        logger.info(f"Initialized VectorStoreManager")
        logger.info(f"Collection: {self.collection_name}")
        logger.info(f"Persist Directory: {self.persist_directory}")
    
    def initialize_chromadb(self, reset: bool = False) -> None:
        """
        Initialize ChromaDB client and collection.
        
        Args:
            reset: If True, deletes existing collection and creates new one
        """
        logger.info("Initializing ChromaDB client...")
        
        try:
            # Initialize persistent client
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info("ChromaDB client initialized successfully")
            
            # Handle reset if requested
            if reset:
                logger.warning(f"Resetting collection: {self.collection_name}")
                try:
                    self.client.delete_collection(name=self.collection_name)
                    logger.info(f"Deleted existing collection: {self.collection_name}")
                except Exception as e:
                    logger.debug(f"No existing collection to delete: {e}")
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Knowledge base for Aastha Co-operative Credit Society",
                    "created_at": datetime.now().isoformat(),
                    "hnsw:space": "cosine"  # Use cosine similarity
                }
            )
            
            logger.info(f"Collection '{self.collection_name}' is ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Add documents with embeddings to ChromaDB collection.
        
        Args:
            documents: List of LangChain Document objects
            embeddings: List of embedding vectors
            batch_size: Number of documents to process per batch
            
        Returns:
            Dictionary with ingestion statistics
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_chromadb() first.")
        
        if len(documents) != len(embeddings):
            raise ValueError(f"Mismatch: {len(documents)} documents but {len(embeddings)} embeddings")
        
        logger.info(f"Adding {len(documents)} documents to collection...")
        
        total_added = 0
        total_skipped = 0
        errors = []
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_docs)} documents)")
            
            try:
                # Prepare data for ChromaDB
                ids = []
                texts = []
                metadatas = []
                batch_embeds = []
                
                for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings)):
                    # Generate unique ID
                    doc_id = self._generate_document_id(doc, i + j)
                    
                    # Prepare metadata (ChromaDB requires all values to be strings, ints, floats, or bools)
                    metadata = self._prepare_metadata(doc.metadata)
                    
                    ids.append(doc_id)
                    texts.append(doc.page_content)
                    metadatas.append(metadata)
                    batch_embeds.append(embedding)
                
                # Add to collection
                self.collection.add(
                    ids=ids,
                    embeddings=batch_embeds,
                    documents=texts,
                    metadatas=metadatas
                )
                
                total_added += len(batch_docs)
                logger.info(f"Successfully added batch {batch_num} ({len(batch_docs)} documents)")
                
            except Exception as e:
                logger.error(f"Error adding batch {batch_num}: {str(e)}")
                errors.append({
                    'batch': batch_num,
                    'error': str(e)
                })
                total_skipped += len(batch_docs)
        
        # Generate statistics
        stats = {
            'total_documents': len(documents),
            'successfully_added': total_added,
            'skipped': total_skipped,
            'errors': errors,
            'collection_name': self.collection_name,
            'persist_directory': str(self.persist_directory)
        }
        
        logger.info(f"Ingestion complete: {total_added} added, {total_skipped} skipped")
        
        return stats
    
    def _generate_document_id(self, doc: Document, index: int) -> str:
        """
        Generate a unique ID for a document.
        
        Args:
            doc: LangChain Document object
            index: Document index in the batch
            
        Returns:
            Unique document ID string
        """
        metadata = doc.metadata
        source_type = metadata.get('source_type', 'unknown')
        
        if source_type == 'website':
            # Use URL + chunk_id
            url = metadata.get('url', '')
            chunk_id = metadata.get('chunk_id', index)
            # Create a safe ID from URL
            url_safe = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('?', '_')
            return f"web_{url_safe}_chunk_{chunk_id}"
        
        elif source_type == 'user_manual':
            # Use section + page + chunk_id
            section = metadata.get('section_title', 'unknown').replace(' ', '_')[:50]
            page = metadata.get('page_number', 0)
            chunk_id = metadata.get('chunk_id', index)
            return f"manual_{section}_page_{page}_chunk_{chunk_id}"
        
        else:
            # Fallback: use source + index
            source = metadata.get('source', 'unknown').replace(' ', '_')
            return f"{source_type}_{source}_doc_{index}"
    
    def _prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare metadata for ChromaDB storage.
        ChromaDB only accepts strings, ints, floats, and bools.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Cleaned metadata dictionary
        """
        clean_metadata = {}
        
        for key, value in metadata.items():
            # Convert None to string
            if value is None:
                clean_metadata[key] = "None"
            # Keep strings, ints, floats, bools as-is
            elif isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            # Convert other types to string
            else:
                clean_metadata[key] = str(value)
        
        # Add ingestion timestamp
        clean_metadata['ingestion_timestamp'] = datetime.now().isoformat()
        
        return clean_metadata
    
    def query_documents(
        self,
        query_texts: List[str],
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the collection for similar documents.
        
        Args:
            query_texts: List of query texts
            query_embeddings: Optional pre-computed query embeddings
            n_results: Number of results to return per query
            where: Metadata filter (e.g., {"source_type": "website"})
            where_document: Document content filter
            
        Returns:
            Query results dictionary
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_chromadb() first.")
        
        logger.info(f"Querying collection with {len(query_texts)} queries")
        
        try:
            if query_embeddings:
                results = self.collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where,
                    where_document=where_document
                )
            else:
                results = self.collection.query(
                    query_texts=query_texts,
                    n_results=n_results,
                    where=where,
                    where_document=where_document
                )
            
            logger.info(f"Query returned {len(results.get('ids', [[]])[0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying collection: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_chromadb() first.")
        
        try:
            # Get collection count
            count = self.collection.count()
            
            # Get sample of documents to analyze metadata
            sample = self.collection.get(limit=min(100, count)) if count > 0 else {'metadatas': []}
            
            # Analyze metadata
            source_types = {}
            categories = {}
            
            for metadata in sample.get('metadatas', []):
                # Count source types
                source_type = metadata.get('source_type', 'unknown')
                source_types[source_type] = source_types.get(source_type, 0) + 1
                
                # Count categories
                category = metadata.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            stats = {
                'collection_name': self.collection_name,
                'total_documents': count,
                'persist_directory': str(self.persist_directory),
                'source_type_distribution': source_types,
                'category_distribution': categories,
                'sample_size': len(sample.get('metadatas', []))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise
    
    def delete_collection(self) -> None:
        """Delete the current collection."""
        if not self.client:
            raise RuntimeError("Client not initialized. Call initialize_chromadb() first.")
        
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            self.collection = None
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
    
    def create_backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the collection metadata.
        
        Args:
            backup_path: Path to save backup. If None, uses default location
            
        Returns:
            Path to backup file
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_chromadb() first.")
        
        try:
            # Default backup path
            if backup_path is None:
                backup_dir = Path("data/backups")
                backup_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"{self.collection_name}_backup_{timestamp}.json"
            
            backup_path = Path(backup_path)
            
            # Get all documents
            all_data = self.collection.get()
            
            # Create backup data
            backup_data = {
                'collection_name': self.collection_name,
                'backup_timestamp': datetime.now().isoformat(),
                'total_documents': len(all_data.get('ids', [])),
                'ids': all_data.get('ids', []),
                'metadatas': all_data.get('metadatas', []),
                # Note: We don't backup embeddings as they can be regenerated
            }
            
            # Save to file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            raise
    
    def print_stats(self) -> None:
        """Print collection statistics in a formatted way."""
        stats = self.get_collection_stats()
        
        print("\n" + "="*80)
        print("CHROMADB COLLECTION STATISTICS")
        print("="*80)
        print(f"\nCollection Name: {stats['collection_name']}")
        print(f"Total Documents: {stats['total_documents']}")
        print(f"Persist Directory: {stats['persist_directory']}")
        
        print(f"\nSource Type Distribution:")
        for source_type, count in stats['source_type_distribution'].items():
            print(f"  - {source_type}: {count}")
        
        print(f"\nCategory Distribution:")
        for category, count in stats['category_distribution'].items():
            print(f"  - {category}: {count}")
        
        print(f"\nSample Size: {stats['sample_size']}")
        print("="*80 + "\n")


def main():
    """Main function to test vector store operations."""
    try:
        print("🗄️  Testing ChromaDB Vector Store Manager")
        print("="*80)
        
        # Initialize vector store
        vs_manager = VectorStoreManager()
        
        # Initialize ChromaDB
        vs_manager.initialize_chromadb(reset=False)
        
        # Get and print statistics
        vs_manager.print_stats()
        
        # Test query (if collection has documents)
        stats = vs_manager.get_collection_stats()
        if stats['total_documents'] > 0:
            print("\n" + "="*80)
            print("TESTING QUERY FUNCTIONALITY")
            print("="*80)
            
            test_queries = [
                "How to add a new user?",
                "What are the deposit schemes?",
                "Fixed deposit interest rates"
            ]
            
            for query in test_queries:
                print(f"\nQuery: '{query}'")
                try:
                    results = vs_manager.query_documents(
                        query_texts=[query],
                        n_results=3
                    )
                    
                    print(f"Results found: {len(results['ids'][0])}")
                    for i, (doc_id, distance, metadata) in enumerate(
                        zip(results['ids'][0], results['distances'][0], results['metadatas'][0]),
                        1
                    ):
                        print(f"\n  [{i}] ID: {doc_id}")
                        print(f"      Distance: {distance:.4f}")
                        print(f"      Source: {metadata.get('source_type', 'unknown')}")
                        print(f"      Category: {metadata.get('category', 'unknown')}")
                        if metadata.get('source_type') == 'website':
                            print(f"      URL: {metadata.get('url', 'N/A')}")
                        else:
                            print(f"      Section: {metadata.get('section_title', 'N/A')}")
                    
                except Exception as e:
                    print(f"  Error: {str(e)}")
            
            print("\n" + "="*80)
        else:
            print("\n⚠️  Collection is empty. Run ingestion pipeline first.")
        
        print("\n✅ Vector Store Manager test complete")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
