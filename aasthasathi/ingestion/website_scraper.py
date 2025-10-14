"""
Website Scraper for myaastha.in

Extracts content from the Aastha Co-operative Credit Society website
including policies, schemes, FAQs, and branch information.
"""

import asyncio
import aiohttp
import time
import sys
import os
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass
import logging
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
from aasthasathi.core.models import Document, DocumentSource


logger = logging.getLogger(__name__)


@dataclass
class ScrapedPage:
    """Represents a scraped web page."""
    url: str
    title: str
    content: str
    metadata: Dict
    links: List[str]
    

class WebsiteScraper:
    """Scraper for myaastha.in website."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.website_base_url
        self.visited_urls: Set[str] = set()
        self.scraped_pages: List[ScrapedPage] = []
        
        # Define important URL patterns to prioritize
        self.priority_patterns = [
            '/about-us/',
            '/how-to-become-a-member/',
            '/scheme/savings-account/',
            '/scheme/recurring-deposits/',
            '/scheme/fixed-deposit/',
            '/scheme/monthly-income/',
            '/personal-loan/',
            '/advance-against-deposits/',
            'loan-against-property/'
        ]
        
        # Define URL patterns to exclude
        self.exclude_patterns = [
            '/admin',
            '/login',
            '/register',
            '/wp-admin',
            '/wp-content/uploads',
            '.pdf',
            '.jpg',
            '.png',
            '.gif',
            '.css',
            '.js'
        ]
    
    async def scrape_website(self, max_pages: int = 50) -> List[Document]:
        """Scrape the website and return processed documents."""
        
        logger.info(f"Starting website scraping for {self.base_url}")
        
        async with aiohttp.ClientSession() as session:
            # Start with homepage
            await self._scrape_page(session, self.base_url)
            
            # Find and scrape important pages
            urls_to_scrape = self._get_priority_urls()
            print(urls_to_scrape)
            
            for url in urls_to_scrape[:max_pages]:
                if url not in self.visited_urls:
                    await self._scrape_page(session, url)
                    await asyncio.sleep(self.settings.scraping_delay)
        
        # Convert scraped pages to documents
        documents = self._convert_to_documents()
        
        logger.info(f"Scraped {len(documents)} documents from website")
        return documents
    
    async def _scrape_page(self, session: aiohttp.ClientSession, url: str) -> Optional[ScrapedPage]:
        """Scrape a single page."""
        
        if url in self.visited_urls or self._should_exclude_url(url):
            return None
        
        try:
            logger.debug(f"Scraping: {url}")
            
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    logger.warning(f"Failed to scrape {url}: Status {response.status}")
                    return None
                
                html = await response.text()
                self.visited_urls.add(url)
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract page content
                page = self._extract_page_content(soup, url)
                
                if page and page.content.strip():
                    self.scraped_pages.append(page)
                    return page
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return None
    
    def _extract_page_content(self, soup: BeautifulSoup, url: str) -> Optional[ScrapedPage]:
        """Extract meaningful content from a page."""
        
        # Get page title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "Untitled"
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'table']):
            element.decompose()
        
        # Extract main content
        content_selectors = [
            'main',
            '.content',
            '.main-content', 
            '.post-content',
            '.entry-content',
            'article',
            '.page-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Clean and extract text
        content = self._clean_text(main_content.get_text())
        
        # Extract links
        links = []
        # for link in main_content.find_all('a', href=True):
        #     href = link['href']
        #     absolute_url = urljoin(url, href)
        #     if self._is_internal_url(absolute_url):
        #         links.append(absolute_url)
        
        # Extract metadata
        metadata = {
            'url': url,
            'title': title,
            'word_count': len(content.split()),
            'extracted_at': time.time()
        }
        
        # Detect content type
        if any(keyword in url.lower() for keyword in ['scheme', 'product', 'deposit', 'loan']):
            metadata['content_type'] = 'scheme_info'
        elif 'faq' in url.lower():
            metadata['content_type'] = 'faq'
        elif 'member' in url.lower():
            metadata['content_type'] = 'membership'
        elif any(keyword in url.lower() for keyword in ['about', 'branch', 'contact']):
            metadata['content_type'] = 'general_info'
        elif any(keyword in url.lower() for keyword in ['policy', 'rule', 'regulation']):
            metadata['content_type'] = 'policy'
        else:
            metadata['content_type'] = 'general'
        
        return ScrapedPage(
            url=url,
            title=title,
            content=content,
            metadata=metadata,
            links=links
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        # Join lines
        cleaned = '\n'.join(lines)
        
        # Remove excessive newlines
        while '\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n', '\n\n')
        
        return cleaned.strip()
    
    def _is_internal_url(self, url: str) -> bool:
        """Check if URL is internal to the website."""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc
    
    def _should_exclude_url(self, url: str) -> bool:
        """Check if URL should be excluded from scraping."""
        return any(pattern in url.lower() for pattern in self.exclude_patterns)
    
    def _get_priority_urls(self) -> List[str]:
        """Get priority URLs to scrape based on discovered links."""
        all_links = []
        
        for page in self.scraped_pages:
            all_links.extend(page.links)
        
        # Prioritize important pages
        priority_urls = []
        other_urls = []
        
        for url in set(all_links):
            if any(pattern in url.lower() for pattern in self.priority_patterns):
                priority_urls.append(url)
            else:
                other_urls.append(url)
        
        for link in self.priority_patterns:
            full_url = urljoin(self.base_url, link)
            if self._is_internal_url(full_url) and full_url not in self.visited_urls:
                if full_url not in priority_urls and full_url not in other_urls:
                    priority_urls.append(full_url)
        
        return priority_urls + other_urls
    
    def _convert_to_documents(self) -> List[Document]:
        """Convert scraped pages to Document objects."""
        documents = []
        
        for i, page in enumerate(self.scraped_pages):
            doc = Document(
                doc_id=f"web_{i+1:04d}",
                title=page.title,
                content=page.content,
                source=DocumentSource.WEBSITE,
                url=page.url,
                metadata=page.metadata
            )
            documents.append(doc)
        
        return documents


async def scrape_website(max_pages: int = 50) -> List[Document]:
    """Main function to scrape the website."""
    scraper = WebsiteScraper()
    return await scraper.scrape_website(max_pages)


# Specific scrapers for different content types
class SchemeScraper:
    """Specialized scraper for scheme/product information."""
    
    @staticmethod
    async def extract_scheme_details(url: str) -> Dict:
        """Extract structured scheme information."""
        # This would extract specific details like:
        # - Interest rates
        # - Minimum amounts
        # - Eligibility criteria
        # - Benefits
        # - Withdrawal rules
        pass


class FAQScraper:
    """Specialized scraper for FAQ content."""
    
    @staticmethod
    async def extract_faq_pairs(url: str) -> List[Dict]:
        """Extract question-answer pairs from FAQ pages."""
        # This would extract structured Q&A pairs
        pass


if __name__ == "__main__":
    # Test the scraper
    async def test_scraper():
        try:
            print("🕷️ Starting website scraper test...")
            print(f"Target website: {get_settings().website_base_url}")
            
            documents = await scrape_website(max_pages=10)  # Reduced for testing
            
            print(f"✅ Successfully scraped {len(documents)} documents")
            
            if documents:
                print("\n📄 Sample documents:")
                for i, doc in enumerate(documents[:3]):
                    print(f"\n{i+1}. Title: {doc.title}")
                    print(f"   URL: {doc.url}")
                    print(f"   Source: {doc.source}")
                    print(f"   Content preview: {doc.content[:150]}...")
                    # print(f"   Content preview: {doc.content}")
                    print("-" * 50)
            else:
                print("⚠️ No documents were scraped. Check website URL and connectivity.")
                
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
    
    # Setup basic logging for testing
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_scraper())