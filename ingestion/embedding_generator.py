"""
Embedding Generator for Document Vectorization

Handles embedding generation using OpenAI's text-embedding-3-small model
with batching, error handling, and cost tracking.
"""

import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generator for creating document embeddings using OpenAI."""
    
    def __init__(self, model: Optional[str] = None, batch_size: int = 100):
        """
        Initialize the Embedding Generator.
        
        Args:
            model: OpenAI embedding model name. If None, uses config default
            batch_size: Number of documents to process per batch
        """
        self.settings = get_settings()
        
        # Set model
        self.model = model or self.settings.embedding_model
        
        # Set batch size
        self.batch_size = batch_size
        
        # Initialize OpenAI embeddings
        try:
            self.embeddings = OpenAIEmbeddings(
                model=self.model,
                openai_api_key=self.settings.openai_api_key,
                dimensions=self.settings.embedding_dimension
            )
            logger.info(f"Initialized EmbeddingGenerator with model: {self.model}")
            logger.info(f"Embedding dimension: {self.settings.embedding_dimension}")
            logger.info(f"Batch size: {self.batch_size}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {str(e)}")
            raise
        
        # Statistics
        self.total_tokens_used = 0
        self.total_documents_processed = 0
        self.total_api_calls = 0
    
    def generate_embeddings_batch(
        self,
        documents: List[Document],
        show_progress: bool = True
    ) -> Tuple[List[List[float]], Dict[str, any]]:
        """
        Generate embeddings for a batch of documents.
        
        Args:
            documents: List of LangChain Document objects
            show_progress: Whether to show progress updates
            
        Returns:
            Tuple of (embeddings list, statistics dict)
        """
        logger.info(f"Generating embeddings for {len(documents)} documents")
        
        all_embeddings = []
        failed_indices = []
        batch_count = 0
        
        start_time = time.time()
        
        # Process in batches
        for i in range(0, len(documents), self.batch_size):
            batch_docs = documents[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(documents) + self.batch_size - 1) // self.batch_size
            
            if show_progress:
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_docs)} documents)")
            
            try:
                # Extract text content from documents
                texts = [doc.page_content for doc in batch_docs]
                
                # Generate embeddings for batch
                batch_embeddings = self._embed_texts_with_retry(texts)
                
                all_embeddings.extend(batch_embeddings)
                batch_count += 1
                
                # Update statistics
                self.total_documents_processed += len(batch_docs)
                self.total_api_calls += 1
                
                # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                batch_tokens = sum(len(text) // 4 for text in texts)
                self.total_tokens_used += batch_tokens
                
                if show_progress:
                    logger.info(f"Batch {batch_num} complete. Estimated tokens: {batch_tokens}")
                
                # Small delay to avoid rate limiting
                if i + self.batch_size < len(documents):
                    time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {str(e)}")
                # Add None embeddings for failed batch
                for j in range(len(batch_docs)):
                    failed_indices.append(i + j)
                    all_embeddings.append(None)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Calculate statistics
        stats = {
            'total_documents': len(documents),
            'successful': len(documents) - len(failed_indices),
            'failed': len(failed_indices),
            'failed_indices': failed_indices,
            'total_batches': total_batches,
            'successful_batches': batch_count,
            'estimated_tokens': self.total_tokens_used,
            'elapsed_time_seconds': elapsed_time,
            'documents_per_second': len(documents) / elapsed_time if elapsed_time > 0 else 0
        }
        
        logger.info(f"Embedding generation complete:")
        logger.info(f"  - Successful: {stats['successful']}/{stats['total_documents']}")
        logger.info(f"  - Failed: {stats['failed']}")
        logger.info(f"  - Time: {elapsed_time:.2f}s")
        logger.info(f"  - Speed: {stats['documents_per_second']:.2f} docs/sec")
        
        return all_embeddings, stats
    
    def _embed_texts_with_retry(
        self,
        texts: List[str],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> List[List[float]]:
        """
        Embed texts with retry logic for handling rate limits and transient errors.
        
        Args:
            texts: List of text strings to embed
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            List of embedding vectors
        """
        for attempt in range(max_retries):
            try:
                embeddings = self.embeddings.embed_documents(texts)
                return embeddings
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if 'rate limit' in error_msg or 'quota' in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limit hit. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Rate limit exceeded and max retries reached")
                        raise
                
                # Check if it's a transient network error
                elif 'timeout' in error_msg or 'connection' in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Network error. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Network error and max retries reached")
                        raise
                
                # Other errors - raise immediately
                else:
                    logger.error(f"Embedding error: {str(e)}")
                    raise
        
        # Should not reach here
        raise RuntimeError("Embedding failed after all retries")
    
    def get_embedding_for_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            self.total_documents_processed += 1
            self.total_api_calls += 1
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding for text: {str(e)}")
            raise
    
    def calculate_embedding_cost(self, total_tokens: Optional[int] = None) -> Dict[str, float]:
        """
        Calculate the estimated cost of embedding generation.
        
        OpenAI text-embedding-3-small pricing (as of 2024):
        $0.020 per 1M tokens
        
        Args:
            total_tokens: Total tokens processed. If None, uses accumulated count
            
        Returns:
            Dictionary with cost information
        """
        tokens = total_tokens or self.total_tokens_used
        
        # Pricing for text-embedding-3-small
        cost_per_million = 0.020
        
        estimated_cost = (tokens / 1_000_000) * cost_per_million
        
        return {
            'total_tokens': tokens,
            'cost_per_million_tokens': cost_per_million,
            'estimated_cost_usd': estimated_cost,
            'model': self.model
        }
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get cumulative statistics for all embedding operations.
        
        Returns:
            Dictionary with statistics
        """
        cost_info = self.calculate_embedding_cost()
        
        return {
            'total_documents_processed': self.total_documents_processed,
            'total_api_calls': self.total_api_calls,
            'total_tokens_used': self.total_tokens_used,
            'estimated_cost_usd': cost_info['estimated_cost_usd'],
            'model': self.model,
            'embedding_dimension': self.settings.embedding_dimension,
            'batch_size': self.batch_size
        }
    
    def print_statistics(self) -> None:
        """Print embedding statistics in a formatted way."""
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("EMBEDDING GENERATOR STATISTICS")
        print("="*80)
        print(f"\nModel: {stats['model']}")
        print(f"Embedding Dimension: {stats['embedding_dimension']}")
        print(f"Batch Size: {stats['batch_size']}")
        print(f"\nDocuments Processed: {stats['total_documents_processed']}")
        print(f"API Calls Made: {stats['total_api_calls']}")
        print(f"Estimated Tokens Used: {stats['total_tokens_used']:,}")
        print(f"Estimated Cost: ${stats['estimated_cost_usd']:.6f} USD")
        print("="*80 + "\n")


def generate_embeddings_for_documents(
    documents: List[Document],
    batch_size: int = 100,
    show_progress: bool = True
) -> Tuple[List[List[float]], Dict[str, any]]:
    """
    Convenience function to generate embeddings for a list of documents.
    
    Args:
        documents: List of LangChain Document objects
        batch_size: Number of documents to process per batch
        show_progress: Whether to show progress updates
        
    Returns:
        Tuple of (embeddings list, statistics dict)
    """
    generator = EmbeddingGenerator(batch_size=batch_size)
    embeddings, stats = generator.generate_embeddings_batch(documents, show_progress)
    
    # Print cost information
    cost_info = generator.calculate_embedding_cost()
    logger.info(f"Estimated cost: ${cost_info['estimated_cost_usd']:.6f} USD")
    
    return embeddings, stats


def main():
    """Main function to test embedding generation."""
    try:
        print("🔢 Testing Embedding Generator")
        print("="*80)
        
        # Create sample documents
        sample_texts = [
            "How to create a new user account in the system?",
            "The Fixed Deposit scheme offers competitive interest rates for various tenures.",
            "Monthly Income Scheme provides regular returns to investors.",
            "Loan application process requires proper documentation and verification.",
            "Branch management involves overseeing daily operations and transactions."
        ]
        
        sample_docs = [
            Document(
                page_content=text,
                metadata={
                    'source': 'test',
                    'source_type': 'test',
                    'index': i
                }
            )
            for i, text in enumerate(sample_texts)
        ]
        
        print(f"\nGenerating embeddings for {len(sample_docs)} sample documents...")
        
        # Initialize generator
        generator = EmbeddingGenerator(batch_size=5)
        
        # Generate embeddings
        embeddings, stats = generator.generate_embeddings_batch(sample_docs, show_progress=True)
        
        # Print results
        print("\n" + "="*80)
        print("EMBEDDING GENERATION RESULTS")
        print("="*80)
        print(f"\nTotal Documents: {len(sample_docs)}")
        print(f"Embeddings Generated: {len([e for e in embeddings if e is not None])}")
        print(f"Failed: {stats['failed']}")
        
        if embeddings and embeddings[0]:
            print(f"\nEmbedding Dimension: {len(embeddings[0])}")
            print(f"Sample Embedding (first 5 values): {embeddings[0][:5]}")
        
        # Print statistics
        generator.print_statistics()
        
        print("✅ Embedding Generator test complete")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
