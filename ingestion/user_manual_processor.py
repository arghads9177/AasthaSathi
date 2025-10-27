"""
PDF Reader for User Manual Processing

Reads the MyAastha User Manual PDF, detects sections and tasks,
and converts them to LangChain Documents for RAG operations.
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFReader:
    """Reader for processing User Manual PDF and extracting structured content."""
    
    def __init__(self, pdf_path: Optional[str] = None):
        """
        Initialize the PDF reader.
        
        Args:
            pdf_path: Path to the PDF file. If None, uses default from data/raw
        """
        self.settings = get_settings()
        
        if pdf_path is None:
            # Default path to User Manual
            self.pdf_path = Path("data/raw/User Manual.pdf")
        else:
            self.pdf_path = Path(pdf_path)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        self.sections = []
        self.doc = None
        
        logger.info(f"Initialized PDFReader for {self.pdf_path}")
    
    def read_pdf(self) -> List[Dict]:
        """
        Read and parse the entire PDF, organizing content by sections and tasks.
        
        Returns:
            List of dictionaries containing section information
        """
        logger.info(f"Reading PDF: {self.pdf_path}")
        
        try:
            self.doc = fitz.open(self.pdf_path)
            logger.info(f"PDF opened successfully. Total pages: {self.doc.page_count}")
            
            # Extract all text with page information
            all_content = self._extract_all_pages()
            
            # Detect and organize sections
            self.sections = self._organize_into_sections(all_content)
            
            logger.info(f"Extracted {len(self.sections)} sections from PDF")
            
            return self.sections
            
        finally:
            if self.doc:
                self.doc.close()
    
    def _extract_all_pages(self) -> List[Tuple[int, str]]:
        """
        Extract text from all pages with page numbers.
        
        Returns:
            List of tuples (page_number, text_content)
        """
        pages_content = []
        
        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]
            text = page.get_text()
            
            # Clean the text
            text = self._clean_text(text)
            
            if text.strip():
                pages_content.append((page_num + 1, text))
        
        logger.info(f"Extracted text from {len(pages_content)} pages")
        return pages_content
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove common PDF artifacts
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\ufeff', '')  # BOM
        
        return text.strip()
    
    def _organize_into_sections(self, pages_content: List[Tuple[int, str]]) -> List[Dict]:
        """
        Organize content into sections and tasks.
        
        Args:
            pages_content: List of (page_number, text) tuples
            
        Returns:
            List of section dictionaries
        """
        sections = []
        current_section = None
        current_task = None
        accumulated_text = []
        
        for page_num, page_text in pages_content:
            lines = page_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                # Check if this is a main section header
                if self._is_main_section(line):
                    # Save previous task/section if exists
                    if current_task:
                        current_task['content'] = '\n'.join(accumulated_text).strip()
                        if current_section:
                            current_section['tasks'].append(current_task)
                        accumulated_text = []
                    
                    if current_section:
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        'section_title': line,
                        'start_page': page_num,
                        'category': self._categorize_section(line),
                        'tasks': []
                    }
                    current_task = None
                    accumulated_text = []
                    logger.debug(f"New section detected: {line} (Page {page_num})")
                
                # Check if this is a task/subsection header (numbered item)
                elif self._is_task_header(line) and current_section:
                    # Save previous task if exists
                    if current_task:
                        current_task['content'] = '\n'.join(accumulated_text).strip()
                        current_section['tasks'].append(current_task)
                        accumulated_text = []
                    
                    # Start new task
                    current_task = {
                        'task_title': line,
                        'page_number': page_num,
                        'content': ''
                    }
                    accumulated_text = [line]
                    logger.debug(f"  New task detected: {line} (Page {page_num})")
                
                else:
                    # Regular content - add to current task or section
                    if current_task or current_section:
                        accumulated_text.append(line)
        
        # Don't forget the last task and section
        if current_task:
            current_task['content'] = '\n'.join(accumulated_text).strip()
            if current_section:
                current_section['tasks'].append(current_task)
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _is_main_section(self, line: str) -> bool:
        """
        Detect if a line is a main section header.
        
        Args:
            line: Text line to check
            
        Returns:
            True if line is a main section header
        """
        # Must be relatively short
        if len(line) > 100 or len(line) < 5:
            return False
        
        # Should not end with punctuation (except colons)
        if line.endswith('.') or line.endswith(','):
            return False
        
        # Should not start with a number (those are tasks)
        if re.match(r'^\d+\.', line):
            return False
        
        # Should start with capital letter
        if not line[0].isupper():
            return False
        
        # Check for keywords indicating main sections
        section_keywords = [
            'management', 'section', 'module', 'scheme', 'account',
            'deposit', 'loan', 'membership', 'branches', 'service points',
            'user', 'bank', 'transaction', 'report', 'dashboard'
        ]
        
        line_lower = line.lower()
        
        # Check if it's title case or has section keywords
        if line.istitle() or any(keyword in line_lower for keyword in section_keywords):
            # Additional check: avoid common non-section phrases
            exclude_phrases = ['note:', 'tip:', 'important:', 'the ', 'each ', 'this ']
            if not any(line_lower.startswith(phrase) for phrase in exclude_phrases):
                return True
        
        return False
    
    def _is_task_header(self, line: str) -> bool:
        """
        Detect if a line is a task/subsection header (numbered).
        
        Args:
            line: Text line to check
            
        Returns:
            True if line is a task header
        """
        # Pattern: "1. Task name" or "1.​Task name"
        if re.match(r'^\d+\.[\s\u200b]', line):
            return True
        
        return False
    
    def _categorize_section(self, section_title: str) -> str:
        """
        Categorize section based on title.
        
        Args:
            section_title: Title of the section
            
        Returns:
            Category string
        """
        title_lower = section_title.lower()
        
        if 'user' in title_lower and 'management' in title_lower:
            return 'user_management'
        elif 'branch' in title_lower or 'service point' in title_lower:
            return 'branch_management'
        elif 'deposit' in title_lower and 'scheme' in title_lower:
            return 'deposit_schemes'
        elif 'loan' in title_lower and 'scheme' in title_lower:
            return 'loan_schemes'
        elif 'bank' in title_lower and 'account' in title_lower:
            return 'bank_accounts'
        elif 'membership' in title_lower:
            return 'membership'
        elif 'transaction' in title_lower:
            return 'transactions'
        elif 'report' in title_lower:
            return 'reports'
        elif 'dashboard' in title_lower:
            return 'dashboard'
        else:
            return 'general'
    
    def convert_to_documents(self, split: bool = True) -> List[Document]:
        """
        Convert extracted sections to LangChain Documents.
        
        Args:
            split: Whether to split documents into chunks (default: True)
            
        Returns:
            List of LangChain Document objects
        """
        if not self.sections:
            logger.warning("No sections found. Run read_pdf() first.")
            return []
        
        logger.info(f"Converting {len(self.sections)} sections to LangChain Documents")
        
        documents = []
        
        for section in self.sections:
            section_title = section['section_title']
            category = section['category']
            start_page = section['start_page']
            
            # If section has tasks, create a document for each task
            if section['tasks']:
                for task in section['tasks']:
                    content = task['content']
                    
                    if not content.strip():
                        continue
                    
                    # Create document with rich metadata
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(self.pdf_path.name),
                            'source_type': 'user_manual',
                            'doc_type': 'pdf',
                            'section_title': section_title,
                            'task_title': task['task_title'],
                            'category': category,
                            'page_number': task['page_number'],
                            'char_count': len(content),
                            'word_count': len(content.split())
                        }
                    )
                    documents.append(doc)
            else:
                # Section without tasks - create single document
                # This shouldn't happen often but handle it
                content = f"{section_title}\n\n(Content starts at page {start_page})"
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': str(self.pdf_path.name),
                        'source_type': 'user_manual',
                        'doc_type': 'pdf',
                        'section_title': section_title,
                        'task_title': section_title,
                        'category': category,
                        'page_number': start_page,
                        'char_count': len(content),
                        'word_count': len(content.split())
                    }
                )
                documents.append(doc)
        
        logger.info(f"Created {len(documents)} LangChain Documents")
        
        if split:
            documents = self._split_documents(documents)
        
        return documents
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks using RecursiveCharacterTextSplitter.
        
        Args:
            documents: List of LangChain Documents to split
            
        Returns:
            List of split LangChain Documents
        """
        logger.info(f"Splitting {len(documents)} documents into chunks")
        
        # Initialize text splitter with configuration from settings
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence ends
                ", ",    # Clause breaks
                " ",     # Word breaks
                ""       # Character breaks (last resort)
            ],
            is_separator_regex=False
        )
        
        # Split documents
        split_docs = text_splitter.split_documents(documents)
        
        # Add chunk information to metadata
        for i, doc in enumerate(split_docs):
            doc.metadata['chunk_id'] = i
            doc.metadata['total_chunks'] = len(split_docs)
        
        logger.info(f"Split into {len(split_docs)} chunks")
        
        return split_docs
    
    def print_sections_summary(self):
        """Print a summary of extracted sections."""
        print("\n" + "="*80)
        print("PDF SECTIONS SUMMARY")
        print("="*80)
        print(f"\nPDF: {self.pdf_path.name}")
        print(f"Total Sections: {len(self.sections)}")
        print("\n" + "-"*80)
        
        for i, section in enumerate(self.sections, 1):
            print(f"\n[{i}] {section['section_title']}")
            print(f"Category: {section['category']}")
            print(f"Start Page: {section['start_page']}")
            print(f"Tasks/Subsections: {len(section['tasks'])}")
            
            if section['tasks']:
                print(f"Task Titles:")
                for j, task in enumerate(section['tasks'][:5], 1):  # Show first 5 tasks
                    print(f"  {j}. {task['task_title'][:80]}...")
                
                if len(section['tasks']) > 5:
                    print(f"  ... and {len(section['tasks']) - 5} more tasks")
            
            print("-" * 80)
        
        print("\n" + "="*80)
        print("END OF SECTIONS SUMMARY")
        print("="*80 + "\n")


def read_pdf_and_create_documents(
    pdf_path: Optional[str] = None,
    split: bool = True
) -> List[Document]:
    """
    Convenience function to read PDF and return LangChain Documents.
    
    Args:
        pdf_path: Path to PDF file. If None, uses default User Manual path
        split: Whether to split documents into chunks (default: True)
        
    Returns:
        List of LangChain Document objects ready for ingestion
    """
    reader = PDFReader(pdf_path)
    reader.read_pdf()
    documents = reader.convert_to_documents(split=split)
    return documents


def main():
    """Main function to test PDF reading."""
    try:
        print("📄 Starting PDF Reader for User Manual")
        print("="*80)
        
        # Initialize reader
        reader = PDFReader()
        
        # Read PDF
        sections = reader.read_pdf()
        
        # Print sections summary
        reader.print_sections_summary()
        
        # Convert to documents
        documents = reader.convert_to_documents(split=True)
        
        # Print document statistics
        print("\n" + "="*80)
        print("LANGCHAIN DOCUMENTS SUMMARY")
        print("="*80)
        print(f"\nTotal documents after splitting: {len(documents)}")
        
        if documents:
            print(f"\nSample chunks (first 3):")
            for i, doc in enumerate(documents[:3], 1):
                print(f"\n[Chunk {i}]")
                print(f"Section: {doc.metadata.get('section_title', 'Unknown')}")
                print(f"Task: {doc.metadata.get('task_title', 'Unknown')}")
                print(f"Category: {doc.metadata.get('category', 'Unknown')}")
                print(f"Page: {doc.metadata.get('page_number', 'Unknown')}")
                print(f"Chunk ID: {doc.metadata.get('chunk_id', 'Unknown')}")
                print(f"Content Length: {len(doc.page_content)} chars")
                print(f"Content Preview:")
                print("-" * 40)
                print(doc.page_content[:400] + "..." if len(doc.page_content) > 400 else doc.page_content)
                print("-" * 80)
        
        print("="*80 + "\n")
        
        return documents
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    documents = main()
    
    if documents:
        print(f"\n✅ Successfully created {len(documents)} LangChain document chunks ready for ingestion")
    else:
        print("\n❌ No documents were created")
