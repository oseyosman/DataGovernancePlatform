"""
Compliance Parser Service
Extracts text from PDFs and finds compliance keywords
Author: Osman Yildiz
"""
import io
import requests
import logging
import PyPDF2
from typing import List, Dict, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceParser:
    """
    Parses PDF documents to extract text and identify compliance keywords.
    """
    
    # Keywords to search for (case-insensitive)
    KEYWORDS = {
        'ISO 27001': ['iso 27001', 'iso/iec 27001', '27001 certified'],
        'ISO 27017': ['iso 27017', 'iso/iec 27017', '27017 certified'],
        'SOC 2': ['soc 2', 'soc2', 'service organization control 2'],
        'Clawback Policy': ['clawback', 'recovery of erroneously awarded compensation', 'erroneously awarded compensation'],
        'GDPR': ['gdpr', 'general data protection regulation'],
        'CCPA': ['ccpa', 'california consumer privacy act'],
        'HIPAA': ['hipaa', 'health insurance portability and accountability act'],
        'PCI DSS': ['pci dss', 'payment card industry data security standard']
    }
    
    def __init__(self):
        self.session = requests.Session()
        # Pretend to be a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_text_from_url(self, url: str) -> Optional[str]:
        """
        Download PDF from URL and extract text.
        
        Args:
            url: URL of the PDF file
            
        Returns:
            Extracted text string or None if failed
        """
        try:
            logger.info(f"Downloading PDF from: {url}")
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Read PDF content
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            # Limit pages to avoid long processing times (e.g., first 50 pages)
            # Many compliance statements are in the beginning or end (10-K Item 1A, 1B, 7, etc.)
            # For 10-K, we might want to scan the whole thing, but let's limit to 100 pages for performance
            max_pages = min(len(reader.pages), 100)
            
            logger.info(f"Extracting text from {max_pages} pages...")
            for i in range(max_pages):
                page = reader.pages[i]
                text += page.extract_text() + "\n"
                
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {e}")
            return None

    def find_keywords(self, text: str) -> Dict[str, bool]:
        """
        Search for compliance keywords in text.
        
        Args:
            text: Text content to search
            
        Returns:
            Dictionary mapping keyword categories to boolean (found/not found)
        """
        if not text:
            return {}
            
        text_lower = text.lower()
        results = {}
        
        for category, search_terms in self.KEYWORDS.items():
            found = False
            for term in search_terms:
                if term in text_lower:
                    found = True
                    break
            results[category] = found
            
        return results

    def analyze_pdf_url(self, url: str) -> Dict[str, bool]:
        """
        Convenience method to download, extract, and analyze a PDF URL.
        
        Args:
            url: URL of the PDF
            
        Returns:
            Dictionary of found keywords
        """
        text = self.extract_text_from_url(url)
        if text:
            return self.find_keywords(text)
        return {}

# Singleton instance
parser = ComplianceParser()
