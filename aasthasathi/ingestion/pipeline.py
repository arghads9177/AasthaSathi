"""
Complete Ingestion Pipeline

Orchestrates the entire data ingestion process from multiple sources
into the vector database.
"""

import asyncio
import logging
import sys
from typing import List, Dict, Optional
from pathlib import Path
import time

# Handle imports for both direct execution and module import
def setup_imports():
    """Setup imports to work with both direct execution and module import."""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Always setup imports first
setup_imports()

from aasthasathi.core.config import get_settings
from aasthasathi.core.models import Document, DocumentSource
from aasthasathi.ingestion.website_scraper import scrape_website
from aasthasathi.ingestion.pdf_processor import process_pdf_directory, process_pdf_file
from aasthasathi.ingestion.vector_database import DocumentIndexer, VectorDatabase


logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Complete data ingestion pipeline."""
    
    def __init__(self):
        self.settings = get_settings()
        self.indexer = DocumentIndexer()
        self.vector_db = VectorDatabase()
        
    async def run_full_ingestion(self, pdf_directory: Optional[str] = None,
                                website_max_pages: int = 50,
                                clear_existing: bool = False) -> Dict[str, int]:
        """Run the complete ingestion pipeline."""
        
        logger.info("Starting full ingestion pipeline")
        start_time = time.time()
        
        results = {
            'website_docs': 0,
            'pdf_docs': 0,
            'total_docs': 0,
            'success': False,
            'duration': 0
        }
        
        try:
            # Clear existing data if requested
            if clear_existing:
                logger.info("Clearing existing vector database")
                self.vector_db.clear_collection()
            
            all_documents = []
            
            # 1. Scrape website
            logger.info("Phase 1: Website scraping")
            website_docs = await self._scrape_website_data(website_max_pages)
            all_documents.extend(website_docs)
            results['website_docs'] = len(website_docs)
            
            # 2. Process PDFs
            if pdf_directory and Path(pdf_directory).exists():
                logger.info("Phase 2: PDF processing")
                pdf_docs = self._process_pdf_data(pdf_directory)
                all_documents.extend(pdf_docs)
                results['pdf_docs'] = len(pdf_docs)
            else:
                logger.info("Phase 2: Skipping PDF processing (no directory provided)")
            
            # 3. Index documents
            logger.info("Phase 3: Vector database indexing")
            if all_documents:
                success = self.indexer.index_documents(all_documents, use_chunking=True)
                results['success'] = success
                results['total_docs'] = len(all_documents)
                
                if success:
                    logger.info(f"Successfully indexed {len(all_documents)} documents")
                else:
                    logger.error("Failed to index documents")
            else:
                logger.warning("No documents to index")
            
            results['duration'] = time.time() - start_time
            
            # Print summary
            self._print_ingestion_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}")
            results['success'] = False
            results['duration'] = time.time() - start_time
            return results
    
    async def _scrape_website_data(self, max_pages: int = 50) -> List[Document]:
        """Scrape website data."""
        
        try:
            logger.info(f"Scraping {self.settings.website_base_url} (max {max_pages} pages)")
            documents = await scrape_website(max_pages)
            logger.info(f"Scraped {len(documents)} documents from website")
            return documents
        except Exception as e:
            logger.error(f"Website scraping failed: {e}")
            return []
    
    def _process_pdf_data(self, pdf_directory: str) -> List[Document]:
        """Process PDF documents."""
        
        try:
            logger.info(f"Processing PDFs from {pdf_directory}")
            documents = process_pdf_directory(pdf_directory, document_type="policy_manual")
            logger.info(f"Processed {len(documents)} documents from PDFs")
            return documents
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return []
    
    def _print_ingestion_summary(self, results: Dict[str, int]):
        """Print ingestion summary."""
        
        print("\n" + "="*60)
        print("🚀 INGESTION PIPELINE SUMMARY")
        print("="*60)
        print(f"📄 Website documents: {results['website_docs']}")
        print(f"📋 PDF documents: {results['pdf_docs']}")
        print(f"📊 Total documents: {results['total_docs']}")
        print(f"⏱️  Duration: {results['duration']:.1f} seconds")
        print(f"✅ Success: {results['success']}")
        
        if results['success']:
            # Show vector database stats
            stats = self.vector_db.get_collection_stats()
            print(f"\n📂 Vector Database Stats:")
            print(f"   Total documents: {stats.get('total_documents', 0)}")
            print(f"   Sources: {stats.get('source_distribution', {})}")
            print(f"   Embedding model: {stats.get('embedding_model', 'Unknown')}")
        
        print("="*60)


class IncrementalIngestion:
    """Handles incremental updates to the knowledge base."""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
    
    async def update_website_content(self, max_pages: int = 10) -> bool:
        """Update website content incrementally."""
        
        logger.info("Starting incremental website update")
        
        try:
            # Scrape recent content
            new_docs = await scrape_website(max_pages)
            
            if new_docs:
                # Check for duplicates and update
                # TODO: Implement duplicate detection based on URL/content hash
                indexer = DocumentIndexer()
                success = indexer.index_documents(new_docs)
                
                logger.info(f"Updated {len(new_docs)} website documents")
                return success
            
            return True
            
        except Exception as e:
            logger.error(f"Incremental website update failed: {e}")
            return False
    
    def add_new_pdf(self, pdf_path: str) -> bool:
        """Add a new PDF document to the knowledge base."""
        
        logger.info(f"Adding new PDF: {pdf_path}")
        
        try:
            # Process new PDF
            documents = process_pdf_file(pdf_path, "policy_manual")
            
            if documents:
                # Index new documents
                indexer = DocumentIndexer()
                success = indexer.index_documents(documents)
                
                logger.info(f"Added {len(documents)} documents from new PDF")
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add new PDF: {e}")
            return False


async def run_ingestion_pipeline(pdf_directory: Optional[str] = None,
                                website_max_pages: int = 50,
                                clear_existing: bool = False) -> Dict[str, int]:
    """Convenience function to run the full ingestion pipeline."""
    
    pipeline = IngestionPipeline()
    return await pipeline.run_full_ingestion(
        pdf_directory=pdf_directory,
        website_max_pages=website_max_pages,
        clear_existing=clear_existing
    )


def test_ingestion_pipeline():
    """Test the ingestion pipeline with sample data."""
    
    async def test():
        logger.info("Testing ingestion pipeline")
        
        # Test with limited data
        results = await run_ingestion_pipeline(
            website_max_pages=5,
            clear_existing=True
        )
        
        print(f"Test results: {results}")
        
        # Test search after ingestion
        if results['success']:
            vector_db = VectorDatabase()
            search_results = vector_db.search_documents(
                "Tell me about Aastha Co-operative Credit Society",
                n_results=3
            )
            
            print(f"\nTest search found {len(search_results)} results:")
            for result in search_results:
                print(f"- {result['metadata'].get('title', 'Unknown')}: {result['similarity']:.3f}")
    
    return asyncio.run(test())


if __name__ == "__main__":
    # Test the pipeline
    test_ingestion_pipeline()