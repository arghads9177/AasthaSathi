"""
Data Ingestion Pipeline

Orchestrates the complete ingestion process:
1. Scrape website content
2. Process user manual PDF
3. Generate embeddings
4. Store in ChromaDB
"""

import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from langchain.schema import Document

from ingestion.web_scraper import scrape_and_create_documents
from ingestion.user_manual_processor import read_pdf_and_create_documents
from ingestion.embedding_generator import EmbeddingGenerator
from ingestion.vector_store import VectorStoreManager
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngestionPipeline:
    """Main pipeline for ingesting data from multiple sources into ChromaDB."""
    
    def __init__(
        self,
        reset_collection: bool = False,
        batch_size: int = 100
    ):
        """
        Initialize the data ingestion pipeline.
        
        Args:
            reset_collection: If True, clears existing collection before ingestion
            batch_size: Number of documents to process per batch
        """
        self.settings = get_settings()
        self.reset_collection = reset_collection
        self.batch_size = batch_size
        
        # Initialize components
        self.vector_store = VectorStoreManager()
        self.embedding_generator = EmbeddingGenerator(batch_size=batch_size)
        
        # Statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_time_seconds': 0,
            'website_docs': 0,
            'manual_docs': 0,
            'total_docs': 0,
            'embeddings_generated': 0,
            'documents_stored': 0,
            'errors': []
        }
        
        logger.info("Initialized DataIngestionPipeline")
        logger.info(f"Reset collection: {reset_collection}")
        logger.info(f"Batch size: {batch_size}")
    
    def run_pipeline(self) -> Dict[str, any]:
        """
        Run the complete ingestion pipeline.
        
        Returns:
            Dictionary with pipeline statistics and results
        """
        self.stats['start_time'] = datetime.now()
        start_time = time.time()
        
        try:
            logger.info("="*80)
            logger.info("STARTING DATA INGESTION PIPELINE")
            logger.info("="*80)
            
            # Step 1: Initialize Vector Store
            logger.info("\n[STEP 1/5] Initializing Vector Store...")
            self.vector_store.initialize_chromadb(reset=self.reset_collection)
            logger.info("✓ Vector Store initialized")
            
            # Step 2: Collect Documents
            logger.info("\n[STEP 2/5] Collecting documents from all sources...")
            all_documents = self._collect_documents()
            self.stats['total_docs'] = len(all_documents)
            logger.info(f"✓ Collected {len(all_documents)} total documents")
            
            # Step 3: Validate Documents
            logger.info("\n[STEP 3/5] Validating documents...")
            valid_documents = self._validate_documents(all_documents)
            logger.info(f"✓ Validated {len(valid_documents)} documents")
            
            if len(valid_documents) == 0:
                logger.error("No valid documents to process!")
                return self._finalize_stats(start_time)
            
            # Step 4: Generate Embeddings
            logger.info("\n[STEP 4/5] Generating embeddings...")
            embeddings, embed_stats = self.embedding_generator.generate_embeddings_batch(
                valid_documents,
                show_progress=True
            )
            self.stats['embeddings_generated'] = embed_stats['successful']
            logger.info(f"✓ Generated {embed_stats['successful']} embeddings")
            
            # Filter out failed embeddings
            valid_docs_with_embeddings = []
            valid_embeddings = []
            for doc, emb in zip(valid_documents, embeddings):
                if emb is not None:
                    valid_docs_with_embeddings.append(doc)
                    valid_embeddings.append(emb)
            
            logger.info(f"Documents with valid embeddings: {len(valid_docs_with_embeddings)}")
            
            # Step 5: Store in ChromaDB
            logger.info("\n[STEP 5/5] Storing documents in ChromaDB...")
            storage_stats = self.vector_store.add_documents(
                documents=valid_docs_with_embeddings,
                embeddings=valid_embeddings,
                batch_size=self.batch_size
            )
            self.stats['documents_stored'] = storage_stats['successfully_added']
            logger.info(f"✓ Stored {storage_stats['successfully_added']} documents")
            
            # Verify storage
            logger.info("\n[VERIFICATION] Checking vector store...")
            collection_stats = self.vector_store.get_collection_stats()
            logger.info(f"✓ Collection contains {collection_stats['total_documents']} documents")
            
            # Create backup
            logger.info("\n[BACKUP] Creating collection backup...")
            try:
                backup_path = self.vector_store.create_backup()
                logger.info(f"✓ Backup created: {backup_path}")
            except Exception as e:
                logger.warning(f"Backup creation failed: {str(e)}")
            
            logger.info("\n" + "="*80)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            self.stats['errors'].append({
                'stage': 'pipeline_execution',
                'error': str(e)
            })
            import traceback
            traceback.print_exc()
        
        return self._finalize_stats(start_time)
    
    def _collect_documents(self) -> List[Document]:
        """
        Collect documents from all sources.
        
        Returns:
            List of all collected documents
        """
        all_documents = []
        
        # Collect from website
        try:
            logger.info("Scraping website...")
            # Run async function
            website_docs = asyncio.run(scrape_and_create_documents(split=True))
            self.stats['website_docs'] = len(website_docs)
            all_documents.extend(website_docs)
            logger.info(f"✓ Collected {len(website_docs)} documents from website")
        except Exception as e:
            logger.error(f"Failed to scrape website: {str(e)}")
            self.stats['errors'].append({
                'source': 'website',
                'error': str(e)
            })
        
        # Collect from user manual
        try:
            logger.info("Processing user manual PDF...")
            manual_docs = read_pdf_and_create_documents(split=True)
            self.stats['manual_docs'] = len(manual_docs)
            all_documents.extend(manual_docs)
            logger.info(f"✓ Collected {len(manual_docs)} documents from user manual")
        except Exception as e:
            logger.error(f"Failed to process user manual: {str(e)}")
            self.stats['errors'].append({
                'source': 'user_manual',
                'error': str(e)
            })
        
        return all_documents
    
    def _validate_documents(self, documents: List[Document]) -> List[Document]:
        """
        Validate documents before processing.
        
        Args:
            documents: List of documents to validate
            
        Returns:
            List of valid documents
        """
        valid_documents = []
        
        for i, doc in enumerate(documents):
            # Check if document has content
            if not doc.page_content or not doc.page_content.strip():
                logger.warning(f"Document {i} has empty content, skipping")
                continue
            
            # Check if document has required metadata
            if not doc.metadata:
                logger.warning(f"Document {i} has no metadata, skipping")
                continue
            
            # Check for source_type
            if 'source_type' not in doc.metadata:
                logger.warning(f"Document {i} missing source_type, skipping")
                continue
            
            valid_documents.append(doc)
        
        skipped = len(documents) - len(valid_documents)
        if skipped > 0:
            logger.warning(f"Skipped {skipped} invalid documents")
        
        return valid_documents
    
    def _finalize_stats(self, start_time: float) -> Dict[str, any]:
        """
        Finalize and return pipeline statistics.
        
        Args:
            start_time: Pipeline start time
            
        Returns:
            Dictionary with complete statistics
        """
        end_time = time.time()
        self.stats['end_time'] = datetime.now()
        self.stats['total_time_seconds'] = end_time - start_time
        
        # Add embedding statistics
        self.stats['embedding_stats'] = self.embedding_generator.get_statistics()
        
        # Add collection statistics
        try:
            self.stats['collection_stats'] = self.vector_store.get_collection_stats()
        except:
            pass
        
        return self.stats
    
    def print_report(self) -> None:
        """Print a comprehensive ingestion report."""
        stats = self.stats
        
        print("\n" + "="*80)
        print("DATA INGESTION PIPELINE REPORT")
        print("="*80)
        
        # Time information
        print(f"\nStart Time: {stats['start_time']}")
        print(f"End Time: {stats['end_time']}")
        print(f"Total Time: {stats['total_time_seconds']:.2f} seconds")
        
        # Document statistics
        print(f"\n--- Document Collection ---")
        print(f"Website Documents: {stats['website_docs']}")
        print(f"User Manual Documents: {stats['manual_docs']}")
        print(f"Total Documents: {stats['total_docs']}")
        
        # Processing statistics
        print(f"\n--- Processing ---")
        print(f"Embeddings Generated: {stats['embeddings_generated']}")
        print(f"Documents Stored: {stats['documents_stored']}")
        
        # Embedding statistics
        if 'embedding_stats' in stats:
            embed_stats = stats['embedding_stats']
            print(f"\n--- Embedding Details ---")
            print(f"Model: {embed_stats['model']}")
            print(f"Dimension: {embed_stats['embedding_dimension']}")
            print(f"Estimated Tokens: {embed_stats['total_tokens_used']:,}")
            print(f"Estimated Cost: ${embed_stats['estimated_cost_usd']:.6f} USD")
        
        # Collection statistics
        if 'collection_stats' in stats:
            coll_stats = stats['collection_stats']
            print(f"\n--- Vector Store ---")
            print(f"Collection Name: {coll_stats['collection_name']}")
            print(f"Total Documents: {coll_stats['total_documents']}")
            print(f"Storage Path: {coll_stats['persist_directory']}")
            
            if coll_stats.get('source_type_distribution'):
                print(f"\nSource Distribution:")
                for source, count in coll_stats['source_type_distribution'].items():
                    print(f"  - {source}: {count}")
            
            if coll_stats.get('category_distribution'):
                print(f"\nCategory Distribution:")
                for category, count in coll_stats['category_distribution'].items():
                    print(f"  - {category}: {count}")
        
        # Errors
        if stats['errors']:
            print(f"\n--- Errors ({len(stats['errors'])}) ---")
            for error in stats['errors']:
                print(f"  - {error.get('source', error.get('stage', 'unknown'))}: {error['error']}")
        
        print("\n" + "="*80)
        
        # Success/failure indicator
        if stats['documents_stored'] > 0:
            print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        else:
            print("❌ PIPELINE FAILED - No documents were stored")
        
        print("="*80 + "\n")


def run_ingestion(reset: bool = False, batch_size: int = 100) -> Dict[str, any]:
    """
    Convenience function to run the complete ingestion pipeline.
    
    Args:
        reset: If True, clears existing collection before ingestion
        batch_size: Number of documents to process per batch
        
    Returns:
        Dictionary with pipeline statistics
    """
    pipeline = DataIngestionPipeline(reset_collection=reset, batch_size=batch_size)
    stats = pipeline.run_pipeline()
    pipeline.print_report()
    return stats


def main():
    """Main function to run the ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run data ingestion pipeline')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset the collection before ingestion'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for processing (default: 100)'
    )
    
    args = parser.parse_args()
    
    print("🚀 AasthaSathi Data Ingestion Pipeline")
    print("="*80)
    
    if args.reset:
        print("⚠️  WARNING: This will delete the existing collection!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Ingestion cancelled.")
            return
    
    # Run pipeline
    stats = run_ingestion(reset=args.reset, batch_size=args.batch_size)
    
    # Return exit code based on success
    if stats['documents_stored'] > 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
