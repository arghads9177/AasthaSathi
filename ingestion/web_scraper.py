"""
Web Scraper for Aastha Co-operative Credit Society Website

Scrapes specified pages from myaastha.in website, extracts and cleans content,
and stores it with proper metadata for RAG operations.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapedPage:
    """Represents a scraped web page with metadata."""
    url: str
    title: str
    content: str
    metadata: Dict
    

class WebScraper:
    """Scraper for Aastha Co-operative Credit Society website."""
    
    def __init__(self):
        """Initialize the web scraper with settings."""
        self.settings = get_settings()
        self.base_url = self.settings.website_base_url
        self.scraped_pages: List[ScrapedPage] = []
        
        # List of pages to scrape
        self.pages_to_scrape = [
            '/about-us/',
            '/how-to-become-a-member/',
            '/scheme/savings-account/',
            '/scheme/recurring-deposits/',
            '/scheme/fixed-deposit/',
            '/scheme/monthly-income/',
            '/personal-loan/',
            '/advance-against-deposits/',
            '/loan-against-property/'
        ]
        
        logger.info(f"Initialized WebScraper for {self.base_url}")
    
    async def scrape_all_pages(self) -> List[ScrapedPage]:
        """Scrape all configured pages."""
        logger.info(f"Starting to scrape {len(self.pages_to_scrape)} pages")
        
        async with aiohttp.ClientSession() as session:
            for page_path in self.pages_to_scrape:
                full_url = urljoin(self.base_url, page_path)
                await self._scrape_page(session, full_url)
                
                # Respect rate limiting
                await asyncio.sleep(self.settings.scraping_delay)
        
        logger.info(f"Successfully scraped {len(self.scraped_pages)} pages")
        return self.scraped_pages
    
    async def _scrape_page(self, session: aiohttp.ClientSession, url: str) -> Optional[ScrapedPage]:
        """Scrape a single page and extract content."""
        try:
            logger.info(f"Scraping: {url}")
            
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: Status {response.status}")
                    return None
                
                html = await response.text()
                
                # Parse HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract and clean content
                page = self._extract_content(soup, url)
                
                if page and page.content.strip():
                    self.scraped_pages.append(page)
                    logger.info(f"Successfully scraped: {page.title}")
                    return page
                else:
                    logger.warning(f"No content extracted from: {url}")
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout while scraping {url}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> Optional[ScrapedPage]:
        """Extract and clean content from HTML."""
        
        # Extract page title
        title = self._extract_title(soup)
        
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)
        
        # Extract main content
        content = self._extract_main_content(soup)
        
        if not content or not content.strip():
            return None
        
        # Clean the content
        content = self._clean_text(content)
        
        if not content or not content.strip():
            return None
        
        # Determine content type and category
        content_type, category = self._categorize_content(url)
        
        # Build metadata
        metadata = {
            'url': url,
            'title': title,
            'content_type': content_type,
            'category': category,
            'word_count': len(content.split()),
            'char_count': len(content),
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'website'
        }
        
        return ScrapedPage(
            url=url,
            title=title,
            content=content,
            metadata=metadata
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try multiple title sources
        title = None
        
        # Try <title> tag
        if soup.title:
            title = soup.title.get_text().strip()
        
        # Try h1 tag
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text().strip()
        
        # Try meta og:title
        if not title:
            meta_title = soup.find('meta', property='og:title')
            if meta_title and meta_title.get('content'):
                title = meta_title['content'].strip()
        
        return title or "Untitled Page"
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """Remove unwanted HTML elements."""
        # Tags to remove completely (be conservative - don't remove header/footer yet)
        unwanted_tags = [
            'script', 'style', 'nav', 'iframe', 'noscript'
        ]
        
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove specific navigation/menu elements by class
        unwanted_selectors = [
            {'class': lambda x: x and 'navigation' in ' '.join(x).lower()},
            {'class': lambda x: x and 'menu' in ' '.join(x).lower() and 'scheme' not in ' '.join(x).lower()},
            {'class': lambda x: x and 'sidebar' in ' '.join(x).lower()},
            {'id': lambda x: x and 'sidebar' in str(x).lower()},
        ]
        
        for selector in unwanted_selectors:
            for element in soup.find_all(**selector):
                element.decompose()
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        main_content = None
        
        # Try specific content areas first
        # 1. Try entry-content (found on this website)
        entry_content = soup.find('div', class_=lambda x: x and 'entry-content' in str(x))
        if entry_content:
            main_content = entry_content
        
        # 2. Try article tag
        if not main_content:
            article = soup.find('article')
            if article:
                main_content = article
        
        # 3. Try main tag
        if not main_content:
            main_tag = soup.find('main')
            if main_tag:
                main_content = main_tag
        
        # 4. Try other common content divs
        if not main_content:
            content_classes = ['content', 'main-content', 'post-content', 'page-content']
            for class_name in content_classes:
                element = soup.find('div', class_=lambda x: x and class_name in str(x).lower())
                if element:
                    main_content = element
                    break
        
        # Fallback to body if no main content found
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Process tables before extracting text
        self._process_tables(main_content)
        
        # Get text content
        text = main_content.get_text(separator='\n', strip=True)
        
        return text
    
    def _process_tables(self, content_element):
        """Convert tables to readable text format or remove them."""
        tables = content_element.find_all('table')
        
        for table in tables:
            try:
                # Extract table data
                table_text = self._table_to_text(table)
                
                if table_text:
                    # Create a text node to replace the table
                    from bs4 import NavigableString
                    table.replace_with(NavigableString(table_text))
                else:
                    # Remove table if we can't extract meaningful data
                    table.decompose()
            except Exception as e:
                logger.warning(f"Error processing table: {e}")
                # Remove problematic table
                table.decompose()
    
    def _table_to_text(self, table) -> str:
        """Convert HTML table to readable text format."""
        rows = table.find_all('tr')
        
        if not rows:
            return ""
        
        # Extract all data
        table_data = []
        for row in rows:
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            # Filter out empty cells
            cell_texts = [text for text in cell_texts if text]
            if cell_texts:
                table_data.append(cell_texts)
        
        if not table_data:
            return ""
        
        # For financial tables, create a more readable format
        formatted_text = "\n\n[RATE TABLE]\n"
        
        # Try to identify structure - look for keywords
        table_str = " ".join([" ".join(row) for row in table_data]).lower()
        is_rate_table = any(keyword in table_str for keyword in ['rate', 'interest', 'tenure', 'deposit', 'months', 'year'])
        
        if is_rate_table:
            # Format as description for better RAG retrieval
            formatted_text += "Interest Rate and Tenure Information:\n"
            
            # Extract key information from cells
            for i, row in enumerate(table_data):
                # Skip header-like rows with just column names
                if len(row) == 1 or (len(row) == 2 and i < 2):
                    continue
                    
                # Look for rows with meaningful data
                row_text = " ".join(row)
                
                # Try to identify if this is a data row (has numbers/percentages)
                has_numbers = any(char.isdigit() or char in ['%', '₹'] for char in row_text)
                
                if has_numbers:
                    formatted_text += f"- {row_text}\n"
        else:
            # Generic table format
            for i, row in enumerate(table_data):
                formatted_text += f"- {' | '.join(row)}\n"
        
        formatted_text += "[END TABLE]\n\n"
        
        return formatted_text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Split into lines
        lines = text.split('\n')
        
        # Clean each line
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Remove lines that are too short (likely navigation/noise)
            if len(line) > 2:
                cleaned_lines.append(line)
        
        # Join lines back
        cleaned = '\n'.join(cleaned_lines)
        
        # Remove excessive whitespace
        while '\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n', '\n\n')
        
        # Remove excessive spaces
        while '  ' in cleaned:
            cleaned = cleaned.replace('  ', ' ')
        
        return cleaned.strip()
    
    def _categorize_content(self, url: str) -> tuple[str, str]:
        """Categorize content based on URL."""
        url_lower = url.lower()
        
        # Determine content type
        if 'scheme' in url_lower or 'deposit' in url_lower:
            content_type = 'financial_product'
            if 'savings' in url_lower:
                category = 'savings_account'
            elif 'recurring' in url_lower:
                category = 'recurring_deposit'
            elif 'fixed' in url_lower:
                category = 'fixed_deposit'
            elif 'monthly-income' in url_lower:
                category = 'monthly_income_scheme'
            else:
                category = 'deposit_scheme'
        
        elif 'loan' in url_lower:
            content_type = 'loan_product'
            if 'personal' in url_lower:
                category = 'personal_loan'
            elif 'property' in url_lower:
                category = 'loan_against_property'
            elif 'deposit' in url_lower:
                category = 'advance_against_deposits'
            else:
                category = 'loan_general'
        
        elif 'member' in url_lower:
            content_type = 'membership_info'
            category = 'membership'
        
        elif 'about' in url_lower:
            content_type = 'organization_info'
            category = 'about_us'
        
        else:
            content_type = 'general'
            category = 'general_info'
        
        return content_type, category
    
    def print_scraped_data(self):
        """Print scraped data for verification."""
        print("\n" + "="*80)
        print(f"SCRAPED DATA SUMMARY")
        print("="*80)
        print(f"\nTotal pages scraped: {len(self.scraped_pages)}")
        print(f"Base URL: {self.base_url}")
        print("\n" + "-"*80)
        
        for i, page in enumerate(self.scraped_pages, 1):
            print(f"\n[{i}] {page.title}")
            print(f"URL: {page.url}")
            print(f"Content Type: {page.metadata['content_type']}")
            print(f"Category: {page.metadata['category']}")
            print(f"Word Count: {page.metadata['word_count']}")
            print(f"Character Count: {page.metadata['char_count']}")
            print(f"Scraped At: {page.metadata['scraped_at']}")
            print(f"\nContent Preview (first 500 chars):")
            print("-" * 40)
            print(page.content[:500] + "..." if len(page.content) > 500 else page.content)
            print("-"*80)
        
        print("\n" + "="*80)
        print("END OF SCRAPED DATA")
        print("="*80 + "\n")


async def main():
    """Main function to run the scraper."""
    try:
        # Initialize scraper
        scraper = WebScraper()
        
        # Scrape all pages
        scraped_pages = await scraper.scrape_all_pages()
        
        # Print results
        scraper.print_scraped_data()
        
        return scraped_pages
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # Run the scraper
    print("🕷️  Starting Web Scraper for Aastha Co-operative Credit Society")
    print("="*80)
    
    scraped_data = asyncio.run(main())
    
    if scraped_data:
        print(f"\n✅ Successfully scraped {len(scraped_data)} pages")
    else:
        print("\n❌ No pages were scraped successfully")
