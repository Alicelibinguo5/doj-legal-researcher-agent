"""Case analysis and information extraction functionality."""

import re
from typing import List, Optional
from bs4 import BeautifulSoup

from .models import CaseInfo, CaseType, Disposition
from .categorizer import ChargeCategorizer
from .utils import setup_logger

logger = setup_logger(__name__)


class CaseAnalyzer:
    """Analyzer for extracting case information from press releases."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.categorizer = ChargeCategorizer()
    
    def analyze_press_release(self, url: str, soup: BeautifulSoup) -> Optional[CaseInfo]:
        """
        Analyze a press release and extract case information.
        
        Args:
            url: URL of the press release
            soup: BeautifulSoup object of the press release
            
        Returns:
            CaseInfo object or None if analysis fails
        """
        try:
            # Extract basic information
            title = self._extract_title(soup)
            date = self._extract_date(soup)
            content = self._extract_content(soup)
            
            # Extract case details
            charges = self._extract_charges(content)
            case_type = self._determine_case_type(title, content)
            defendant_name = self._extract_defendant_name(content)
            location = self._extract_location(content)
            disposition = self._determine_disposition(title, content)
            description = self._create_description(content)
            
            # Categorize charges
            charge_categories = self.categorizer.categorize_charges(charges, content)
            
            return CaseInfo(
                title=title,
                date=date,
                url=url,
                charges=charges,
                case_type=case_type,
                defendant_name=defendant_name,
                location=location,
                disposition=disposition,
                description=description,
                charge_categories=charge_categories
            )
            
        except Exception as e:
            logger.error(f"Error analyzing press release {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from press release."""
        title_selectors = ['h1', 'title', '.page-title', '.headline']
        
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        
        return "Unknown"
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract date from press release."""
        date_selectors = [
            'time',
            '.date',
            '.publish-date',
            '.article-date',
            '[class*="date"]',
            '[class*="time"]'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                # Try to get datetime attribute first
                date_text = elem.get('datetime') or elem.get_text().strip()
                if date_text:
                    return date_text
        
        return "Unknown"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from press release."""
        content_selectors = [
            '.content',
            '.article-content',
            '.body',
            '.press-release-content',
            'article',
            'main'
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text()
        
        # Fallback to all text
        return soup.get_text()
    
    def _extract_charges(self, content: str) -> List[str]:
        """Extract charges from press release content."""
        charges = []
        
        # Common charge patterns
        charge_patterns = [
            r'charged with ([^.]+)',
            r'indicted (?:on|for) ([^.]+)',
            r'convicted of ([^.]+)',
            r'pleaded guilty to ([^.]+)',
            r'pled guilty to ([^.]+)',
            r'count(?:s)? of ([^.]+)',
            r'violation of ([^.]+)',
            r'sentenced for ([^.]+)',
            r'guilty of ([^.]+)',
        ]
        
        for pattern in charge_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                charge = self._clean_charge_text(match)
                if self._is_valid_charge(charge) and charge not in charges:
                    charges.append(charge)
        
        return charges
    
    def _clean_charge_text(self, text: str) -> str:
        """Clean up extracted charge text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common trailing words
        trailing_words = ['and', 'or', 'including', 'among others', 'etc']
        for word in trailing_words:
            if text.lower().endswith(word):
                text = text[:-len(word)].strip()
        
        # Remove trailing punctuation except periods that end sentences
        text = re.sub(r'[,;:]$', '', text)
        
        return text
    
    def _is_valid_charge(self, charge: str) -> bool:
        """Check if extracted text is a valid charge."""
        # Must be longer than 5 characters
        if len(charge) < 5:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', charge):
            return False
        
        # Should not be too long (likely extracted too much)
        if len(charge) > 200:
            return False
        
        # Filter out common false positives
        false_positives = [
            'the united states',
            'the defendant',
            'the court',
            'the government',
            'according to',
            'press release'
        ]
        
        charge_lower = charge.lower()
        for fp in false_positives:
            if fp in charge_lower:
                return False
        
        return True
    
    def _determine_case_type(self, title: str, content: str) -> CaseType:
        """Determine the type of case."""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ['indictment', 'indicted', 'criminal', 'convicted']):
            return CaseType.CRIMINAL
        elif any(word in text for word in ['civil', 'lawsuit', 'settlement']):
            return CaseType.CIVIL
        elif any(word in text for word in ['guilty', 'plea', 'pleaded', 'pled']):
            return CaseType.PLEA
        else:
            return CaseType.UNKNOWN
    
    def _extract_defendant_name(self, content: str) -> str:
        """Extract defendant name from content."""
        # Name patterns (simplified - would benefit from NER)
        name_patterns = [
            r'(?:defendant|accused|individual)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(?:of|from|aged?)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+\d+',  # Name followed by age
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+was\s+(?:sentenced|convicted|charged)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, content)
            if match:
                name = match.group(1).strip()
                # Filter out common false positives
                if not self._is_likely_name(name):
                    continue
                return name
        
        return "Unknown"
    
    def _is_likely_name(self, name: str) -> bool:
        """Check if extracted text is likely a person's name."""
        # Filter out common false positives
        false_positives = [
            'United States', 'Justice Department', 'Attorney General',
            'District Attorney', 'Special Agent', 'Chief Judge',
            'Northern District', 'Southern District', 'Eastern District',
            'Western District', 'Press Release', 'News Release'
        ]
        
        return name not in false_positives
    
    def _extract_location(self, content: str) -> str:
        """Extract location information."""
        location_patterns = [
            r'(?:District of|Eastern District|Western District|Northern District|Southern District)\s+([A-Z][a-z]+)',
            r'(?:in|of)\s+([A-Z][a-z]+,\s+[A-Z]{2})',
            r'U\.S\.\s+Attorney[^,]+,\s+([^,]+)',
            r'(?:located|based|residing)\s+in\s+([A-Z][a-z]+(?:,\s+[A-Z]{2})?)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        
        return "Unknown"
    
    def _determine_disposition(self, title: str, content: str) -> Disposition:
        """Determine case disposition."""
        text = (title + " " + content).lower()
        
        if 'sentenced' in text or 'sentencing' in text:
            return Disposition.SENTENCED
        elif 'convicted' in text or 'conviction' in text:
            return Disposition.CONVICTED
        elif 'indicted' in text or 'indictment' in text:
            return Disposition.INDICTED
        elif ('guilty' in text and 'plea' in text) or 'pleaded' in text or 'pled' in text:
            return Disposition.GUILTY_PLEA
        elif 'arrested' in text:
            return Disposition.ARRESTED
        else:
            return Disposition.UNKNOWN
    
    def _create_description(self, content: str, max_length: int = 500) -> str:
        """Create a description from content."""
        # Clean up content
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content