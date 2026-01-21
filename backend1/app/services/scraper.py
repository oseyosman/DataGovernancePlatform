"""
AnnualReports.com Web Scraper Service
Author: Osman Yildiz

This module provides functionality to scrape company data and annual reports
from AnnualReports.com.
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnnualReportsScraper:
    """Scraper for AnnualReports.com"""
    
    BASE_URL = "https://www.annualreports.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    def __init__(self, rate_limit_delay=1.0):
        """
        Initialize the scraper
        
        Args:
            rate_limit_delay: Delay in seconds between requests to respect rate limiting
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make a GET request and return parsed HTML
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            logger.info(f"Fetching: {url}")
            time.sleep(self.rate_limit_delay)  # Rate limiting
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'lxml')
        
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def scrape_company(self, company_slug: str) -> Optional[Dict]:
        """
        Scrape company information from a company page
        
        Args:
            company_slug: Company identifier in URL (e.g., 'apple-inc')
            
        Returns:
            Dictionary containing company data or None if scraping failed
        """
        url = f"{self.BASE_URL}/Company/{company_slug}"
        soup = self._make_request(url)
        
        if not soup:
            return None
        
        try:
            company_data = {
                'source_url': url,
                'slug': company_slug,
                'name': None,
                'ticker': None,
                'exchange': None,
                'industry': None,
                'sector': None,
                'description': None,
                'employee_count': None,
                'website': None,
                'annual_reports': []
            }
            
            # Extract company name
            name_elem = soup.find('h1')
            if name_elem:
                company_data['name'] = name_elem.get_text(strip=True)
            
            # Extract ticker and exchange
            ticker_elem = soup.find('span', string=re.compile(r'Ticker\s*:', re.I))
            if ticker_elem:
                ticker_text = ticker_elem.find_next_sibling(text=True)
                if ticker_text:
                    company_data['ticker'] = ticker_text.strip()
            
            exchange_elem = soup.find('span', string=re.compile(r'Exchange\s*:', re.I))
            if exchange_elem:
                exchange_text = exchange_elem.find_next_sibling(text=True)
                if exchange_text:
                    company_data['exchange'] = exchange_text.strip()
            
            # Extract industry/sector
            industry_elem = soup.find('span', string=re.compile(r'Industry\s*:', re.I))
            if industry_elem:
                industry_text = industry_elem.find_next_sibling(text=True)
                if industry_text:
                    company_data['industry'] = industry_text.strip()
            
            sector_elem = soup.find('span', string=re.compile(r'Sector\s*:', re.I))
            if sector_elem:
                sector_text = sector_elem.find_next_sibling(text=True)
                if sector_text:
                    company_data['sector'] = sector_text.strip()
            
            # Extract company description/overview
            overview_section = soup.find('div', class_=re.compile(r'overview', re.I))
            if overview_section:
                paragraphs = overview_section.find_all('p')
                if paragraphs:
                    company_data['description'] = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # Alternative: look for meta description
            if not company_data['description']:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    company_data['description'] = meta_desc['content']
            
            # Extract website link
            website_link = soup.find('a', string=re.compile(r'Visit website', re.I))
            if website_link and website_link.get('href'):
                company_data['website'] = website_link['href']
            
            # Extract annual reports
            company_data['annual_reports'] = self._extract_annual_reports(soup)
            
            logger.info(f"Successfully scraped company: {company_data['name']}")
            return company_data
            
        except Exception as e:
            logger.error(f"Error parsing company data for {company_slug}: {e}")
            return None
    
    def _extract_annual_reports(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract annual report information from company page
        
        Args:
            soup: BeautifulSoup object of company page
            
        Returns:
            List of dictionaries containing report data
        """
        reports = []
        
        try:
            # Find all report year sections
            report_sections = soup.find_all('div', class_=re.compile(r'report|annual', re.I))
            
            # Also try finding by looking for year patterns
            year_pattern = re.compile(r'(19|20)\d{2}')
            
            # Look for report links
            report_links = soup.find_all('a', href=re.compile(r'HostedData/AnnualReportArchive', re.I))
            
            for link in report_links:
                try:
                    report_data = {
                        'title': None,
                        'year': None,
                        'report_type': 'Annual Report',
                        'pdf_url': None,
                        'html_url': None,
                        'view_url': None
                    }
                    
                    # Extract URL
                    href = link.get('href')
                    if href:
                        if not href.startswith('http'):
                            href = self.BASE_URL + href if href.startswith('/') else self.BASE_URL + '/' + href
                        
                        if 'pdf' in href.lower():
                            report_data['pdf_url'] = href
                        else:
                            report_data['view_url'] = href
                    
                    # Extract text and year
                    link_text = link.get_text(strip=True)
                    report_data['title'] = link_text
                    
                    # Try to extract year from text
                    year_match = year_pattern.search(link_text)
                    if year_match:
                        report_data['year'] = int(year_match.group())
                    
                    # Look for parent container to get more info
                    parent = link.find_parent('div')
                    if parent:
                        parent_text = parent.get_text()
                        
                        # Try to find year in parent text if not found yet
                        if not report_data['year']:
                            year_match = year_pattern.search(parent_text)
                            if year_match:
                                report_data['year'] = int(year_match.group())
                        
                        # Check for download button
                        download_link = parent.find('a', string=re.compile(r'Download', re.I))
                        if download_link and download_link.get('href'):
                            download_href = download_link['href']
                            if not download_href.startswith('http'):
                                download_href = self.BASE_URL + download_href if download_href.startswith('/') else self.BASE_URL + '/' + download_href
                            report_data['pdf_url'] = download_href
                    
                    # Only add if we have a year
                    if report_data['year']:
                        reports.append(report_data)
                
                except Exception as e:
                    logger.warning(f"Error extracting report data: {e}")
                    continue
            
            # Remove duplicates based on year
            seen_years = set()
            unique_reports = []
            for report in reports:
                if report['year'] not in seen_years:
                    seen_years.add(report['year'])
                    unique_reports.append(report)
            
            logger.info(f"Extracted {len(unique_reports)} annual reports")
            return unique_reports
            
        except Exception as e:
            logger.error(f"Error extracting annual reports: {e}")
            return []
    
    def search_companies(self, query: str) -> List[Dict]:
        """
        Search for companies on AnnualReports.com
        
        Args:
            query: Search query (company name or ticker)
            
        Returns:
            List of company results
        """
        url = f"{self.BASE_URL}/Companies?search={query}"
        soup = self._make_request(url)
        
        if not soup:
            return []
        
        companies = []
        
        try:
            # Find company links in search results
            company_links = soup.find_all('a', href=re.compile(r'/Company/', re.I))
            
            for link in company_links:
                try:
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # Extract company slug
                    slug_match = re.search(r'/Company/([^/]+)', href)
                    if not slug_match:
                        continue
                    
                    slug = slug_match.group(1)
                    name = link.get_text(strip=True)
                    
                    companies.append({
                        'slug': slug,
                        'name': name,
                        'url': self.BASE_URL + href if not href.startswith('http') else href
                    })
                
                except Exception as e:
                    logger.warning(f"Error parsing company search result: {e}")
                    continue
            
            logger.info(f"Found {len(companies)} companies for query: {query}")
            return companies
            
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return []


# Convenience functions for direct use
def scrape_company_by_slug(slug: str) -> Optional[Dict]:
    """
    Scrape a single company by its slug
    
    Args:
        slug: Company slug (e.g., 'apple-inc')
        
    Returns:
        Company data dictionary or None
    """
    scraper = AnnualReportsScraper()
    return scraper.scrape_company(slug)


def search_companies(query: str) -> List[Dict]:
    """
    Search for companies
    
    Args:
        query: Search query
        
    Returns:
        List of company results
    """
    scraper = AnnualReportsScraper()
    return scraper.search_companies(query)
