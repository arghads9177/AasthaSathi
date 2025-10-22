"""
PDF Processing Module for AasthaSathi

Handles PDF document loading, text extraction, and chunking
for policy manuals and procedural documents.
"""

try:
    import fitz  # PyMuPDF
except Exception as e:
    raise ImportError(
        "PyMuPDF (fitz) is required to run the PDF processor.\n"
        "Install it with: pip install PyMuPDF\n"
        f"Original error: {e}"
    )
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import hashlib
from dataclasses import dataclass
import sys
import os
from pathlib import Path

# Handle imports for both direct execution and module import
def setup_imports():
    """Setup imports to work with both direct execution and module import."""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Always setup imports first
setup_imports()

# Now import with absolute imports
from aasthasathi.core.config import get_settings
from aasthasathi.core.models import Document, DocumentSource, DocumentChunk

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangChainDocument


logger = logging.getLogger(__name__)


@dataclass
class PDFSection:
    """Represents a section within a PDF document."""
    title: str
    content: str
    page_start: int
    page_end: int
    level: int  # Heading level (1-6)


class PDFProcessor:
    """Processes PDF documents for knowledge base ingestion."""
    
    def __init__(self):
        self.settings = get_settings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_pdf(self, pdf_path: str, document_type: str = "manual") -> List[Document]:
        """Process a PDF file and return Document objects."""
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            # Extract text and metadata from PDF
            pdf_content = self._extract_pdf_content(pdf_path)
            
            # Detect document structure
            sections = self._detect_sections(pdf_content)
            
            # Create documents from sections or full text
            if sections:
                documents = self._create_documents_from_sections(
                    sections, pdf_path, document_type
                )
            else:
                documents = self._create_document_from_full_text(
                    pdf_content, pdf_path, document_type
                )
            
            logger.info(f"Created {len(documents)} documents from PDF")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return []
    
    def _extract_pdf_content(self, pdf_path: str) -> Dict:
        """Extract text content and metadata from PDF."""
        
        doc = fitz.open(pdf_path)
        
        content = {
            'pages': [],
            'metadata': doc.metadata,
            'page_count': len(doc),
            'file_path': pdf_path,
            'file_name': Path(pdf_path).name
        }
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text
            text = page.get_text()
            
            # Extract images info (if needed for context)
            images = page.get_images()
            
            # Extract tables (basic detection)
            tables = self._detect_tables_on_page(page)
            
            page_content = {
                'page_number': page_num + 1,
                'text': text,
                'images_count': len(images),
                'tables': tables,
                'char_count': len(text)
            }
            
            content['pages'].append(page_content)
        
        doc.close()
        return content
    
    def _detect_tables_on_page(self, page) -> List[Dict]:
        """Detect and extract table content from a page."""
        tables = []
        
        try:
            # Find tables using PyMuPDF
            table_list = page.find_tables()
            
            for table in table_list:
                table_data = table.extract()
                if table_data:
                    tables.append({
                        'data': table_data,
                        'bbox': table.bbox,
                        'rows': len(table_data),
                        'cols': len(table_data[0]) if table_data else 0
                    })
        except Exception as e:
            logger.debug(f"Table detection failed: {e}")
        
        return tables
    
    def _detect_sections(self, pdf_content: Dict) -> List[PDFSection]:
        """Detect document sections based on headings and structure."""
        
        sections = []
        current_section = None
        
        for page in pdf_content['pages']:
            lines = page['text'].split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                if not line:
                    continue
                
                # Detect headings based on patterns
                heading_level = self._detect_heading_level(line, lines, line_num)
                
                if heading_level > 0:
                    # Save previous section
                    if current_section:
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = PDFSection(
                        title=line,
                        content="",
                        page_start=page['page_number'],
                        page_end=page['page_number'],
                        level=heading_level
                    )
                elif current_section:
                    # Add content to current section
                    current_section.content += line + "\n"
                    current_section.page_end = page['page_number']
        
        # Add last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _detect_heading_level(self, line: str, lines: List[str], line_num: int) -> int:
        """Detect if a line is a heading and its level."""
        
        # Pattern 1: All caps with limited length (likely heading)
        if (line.isupper() and 
            len(line) < 100 and 
            len(line.split()) <= 10 and
            not line.endswith('.')):
            return 1
        
        # Pattern 2: Title case with specific patterns
        if (line.istitle() and 
            len(line) < 80 and
            len(line.split()) <= 8 and
            not line.endswith('.')):
            return 2
        
        # Pattern 3: Numbered sections (1., 1.1, A., etc.)
        if self._is_numbered_heading(line):
            return self._get_numbering_level(line)
        
        # Pattern 4: Bold or emphasized text (would need format detection)
        # For now, we'll use heuristics
        
        return 0
    
    def _is_numbered_heading(self, line: str) -> bool:
        """Check if line is a numbered heading."""
        import re
        
        patterns = [
            r'^\d+\.\s+[A-Z]',  # 1. Introduction
            r'^\d+\.\d+\s+[A-Z]',  # 1.1 Overview
            r'^[A-Z]\.\s+[A-Z]',  # A. Section
            r'^\([a-z]\)\s+[A-Z]',  # (a) Subsection
            r'^[IVX]+\.\s+[A-Z]',  # Roman numerals
        ]
        
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _get_numbering_level(self, line: str) -> int:
        """Get the hierarchical level of a numbered heading."""
        import re
        
        if re.match(r'^\d+\.\s+', line):
            return 1
        elif re.match(r'^\d+\.\d+\s+', line):
            return 2
        elif re.match(r'^\d+\.\d+\.\d+\s+', line):
            return 3
        elif re.match(r'^[A-Z]\.\s+', line):
            return 2
        elif re.match(r'^\([a-z]\)\s+', line):
            return 3
        
        return 1
    
    def _create_documents_from_sections(self, sections: List[PDFSection], 
                                      pdf_path: str, document_type: str) -> List[Document]:
        """Create Document objects from PDF sections."""
        
        documents = []
        
        for i, section in enumerate(sections):
            if not section.content.strip():
                continue
            
            doc_id = f"pdf_{Path(pdf_path).stem}_{i+1:03d}"
            
            doc = Document(
                doc_id=doc_id,
                title=section.title,
                content=section.content.strip(),
                source=DocumentSource.PDF_MANUAL,
                page_number=section.page_start,
                section=section.title,
                metadata={
                    'file_path': pdf_path,
                    'file_name': Path(pdf_path).name,
                    'document_type': document_type,
                    'section_level': section.level,
                    'page_start': section.page_start,
                    'page_end': section.page_end,
                    'word_count': len(section.content.split())
                }
            )
            
            documents.append(doc)
        
        return documents
    
    def _create_document_from_full_text(self, pdf_content: Dict, 
                                      pdf_path: str, document_type: str) -> List[Document]:
        """Create Document objects from full PDF text."""
        
        # Combine all page text
        full_text = ""
        for page in pdf_content['pages']:
            full_text += page['text'] + "\n\n"
        
        doc_id = f"pdf_{Path(pdf_path).stem}_full"
        
        doc = Document(
            doc_id=doc_id,
            title=pdf_content['file_name'],
            content=full_text.strip(),
            source=DocumentSource.PDF_MANUAL,
            metadata={
                'file_path': pdf_path,
                'file_name': pdf_content['file_name'],
                'document_type': document_type,
                'page_count': pdf_content['page_count'],
                'total_chars': len(full_text),
                'word_count': len(full_text.split())
            }
        )
        
        return [doc]
    
    def create_chunks(self, documents: List[Document]) -> List[DocumentChunk]:
        """Create chunks from documents for vector storage."""
        
        chunks = []
        
        for doc in documents:
            # Use LangChain text splitter
            langchain_doc = LangChainDocument(
                page_content=doc.content,
                metadata=doc.metadata
            )
            
            split_docs = self.text_splitter.split_documents([langchain_doc])
            
            for i, split_doc in enumerate(split_docs):
                chunk_id = f"{doc.doc_id}_chunk_{i+1:03d}"
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc.doc_id,
                    content=split_doc.page_content,
                    chunk_index=i,
                    metadata={
                        **doc.metadata,
                        'chunk_size': len(split_doc.page_content),
                        'chunk_words': len(split_doc.page_content.split())
                    }
                )
                
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks


class PDFBatchProcessor:
    """Batch process multiple PDF files."""
    
    def __init__(self):
        self.processor = PDFProcessor()
    
    def process_directory(self, directory_path: str, 
                         document_type: str = "manual") -> List[Document]:
        """Process all PDF files in a directory."""
        
        directory = Path(directory_path)
        pdf_files = list(directory.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        all_documents = []
        
        for pdf_file in pdf_files:
            try:
                documents = self.processor.process_pdf(str(pdf_file), document_type)
                all_documents.extend(documents)
                logger.info(f"Processed {pdf_file.name}: {len(documents)} documents")
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
        
        return all_documents


def process_pdf_file(pdf_path: str, document_type: str = "manual") -> List[Document]:
    """Convenience function to process a single PDF file."""
    processor = PDFProcessor()
    return processor.process_pdf(pdf_path, document_type)


def process_pdf_directory(directory_path: str, document_type: str = "manual") -> List[Document]:
    """Convenience function to process all PDFs in a directory."""
    batch_processor = PDFBatchProcessor()
    return batch_processor.process_directory(directory_path, document_type)


if __name__ == "__main__":
    # Test the PDF processor by using the project's data/raw/User Manual.pdf
    logging.basicConfig(level=logging.INFO)
    project_root = Path(__file__).resolve().parents[2]
    default_pdf = project_root / "data" / "raw" / "User Manual.pdf"

    documents = []

    if default_pdf.is_file():
        print(f"🔎 Found default PDF at: {default_pdf}")
        documents = process_pdf_file(str(default_pdf))
    else:
        # Fallback: process all PDFs in data/raw if the specific file isn't present
        raw_dir = project_root / "data" / "raw"
        if raw_dir.exists() and any(raw_dir.glob("*.pdf")):
            print(f"⚠️ Specific file not found, processing all PDFs in: {raw_dir}")
            documents = process_pdf_directory(str(raw_dir))
        else:
            print(f"❌ No PDF found at {default_pdf} and no PDFs in {raw_dir}")
            print("Please add 'User Manual.pdf' to data/raw or provide a PDF path.")
            sys.exit(1)

    print(f"Processed {len(documents)} documents")
    for doc in documents[:5]:
        print(f"\nTitle: {doc.title}")
        print(f"Source: {doc.source}")
        print(f"Content preview: {doc.content[:200]}...")