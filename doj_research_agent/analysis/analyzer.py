"""Case analysis and information extraction functionality."""

import re
import json
from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
from ..core.models import CaseInfo, CaseType, Disposition, CaseFraudInfo
from .categorizer import ChargeCategorizer
from ..core.utils import setup_logger
import os
from ..core.constants import FRAUD_KEYWORDS

try:
    import openai
except ImportError:
    openai = None

logger = setup_logger(__name__)


class CaseAnalyzer:
    """Analyzer for extracting case information from press releases."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.categorizer = ChargeCategorizer()
    
    def _is_fraud_case(self, charge_categories, content: str) -> CaseFraudInfo:
        """
        Determine if a case is fraud based on charge categories or content.
        Returns a CaseFraudInfo object.
        """
        # Use FRAUD_KEYWORDS from constants.py for all fraud keyword checks
        fraud_keywords = set()
        for v in FRAUD_KEYWORDS.values():
            if isinstance(v, list):
                fraud_keywords.update(v)
            elif isinstance(v, set):
                fraud_keywords.update(list(v))
        
        # Check charge categories for fraud-related categories
        fraud_categories = {
            'financial_fraud', 'health_care_fraud', 'disaster_fraud', 
            'consumer_protection', 'cybercrime', 'false_claims_act',
            'public_corruption', 'tax', 'immigration', 'intellectual_property'
        }
        
        category_fraud = any(cat.value in fraud_categories for cat in charge_categories)
        
        # Check content for fraud keywords
        content_lower = content.lower()
        found_keywords = []
        for keyword in fraud_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        # Determine if this is a fraud case
        is_fraud = category_fraud or len(found_keywords) > 0
        
        # Find evidence snippet
        evidence = None
        if is_fraud and found_keywords:
            # Find the first occurrence of any fraud keyword
            first_keyword = found_keywords[0]
            idx = content_lower.find(first_keyword)
            if idx != -1:
                start = max(0, idx - 60)
                end = min(len(content), idx + 60)
                evidence = content[start:end].strip()
                # Add context about which keywords were found
                evidence = f"Keywords found: {', '.join(found_keywords[:3])} - {evidence}"
        
        return CaseFraudInfo(
            is_fraud=is_fraud, 
            charge_categories=charge_categories, 
            evidence=evidence
        )

    def _is_money_laundering_case(self, content: str):
        """
        Determine if a case involves money laundering based on content.
        Returns a dict with is_money_laundering (bool) and evidence (str or None).
        """
        # Money laundering specific keywords (do NOT include these in fraud_keywords)
        laundering_keywords = {
            'money laundering', 'laundering', 'laundered', 'launder',
            'cleaning money', 'proceeds of crime', 'illicit funds',
            'placement', 'layering', 'integration',
            'smurfing', 'structuring', 'shell company',
            'front company', 'offshore account', 'hawala',
            'bulk cash', 'wire transfer', 'bank secrecy',
            'anti-money laundering', 'aml', 'financial crimes enforcement network',
            'finCEN', 'suspicious activity report', 'sar',
            'currency transaction report', 'ctr',
            'unexplained wealth', 'concealment of proceeds',
            'illegal proceeds', 'dirty money', 'clean money',
        }
        content_lower = content.lower()
        found_keywords = []
        for keyword in laundering_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        is_laundering = len(found_keywords) > 0
        evidence = None
        if is_laundering and found_keywords:
            first_keyword = found_keywords[0]
            idx = content_lower.find(first_keyword)
            if idx != -1:
                start = max(0, idx - 60)
                end = min(len(content), idx + 60)
                evidence = content[start:end].strip()
                evidence = f"Keywords found: {', '.join(found_keywords[:3])} - {evidence}"
        return {"is_money_laundering": is_laundering, "evidence": evidence}

    def extract_main_article_content(self, soup: BeautifulSoup) -> str:
        # Try <article> tag first
        article = soup.find('article')
        if article:
            # Try all <p> tags inside article
            paragraphs = [p.get_text(separator=' ', strip=True) for p in article.find_all('p')]
            content = ' '.join(paragraphs).strip()
            if content and 'Archived News' not in content and len(content) > 100:
                return content
            # Fallback to all text in article
            text = article.get_text(separator=' ', strip=True)
            if text and 'Archived News' not in text and len(text) > 100:
                return text
        # Fallback to common DOJ content selectors
        for selector in [
            '.field--name-body', '.field--type-text-with-summary',
            '.press-release-content', '.content', '.article-content'
        ]:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(separator=' ', strip=True)
                if text and 'Archived News' not in text and len(text) > 100:
                    return text
        # Fallback to all text (last resort)
        text = soup.get_text(separator=' ', strip=True)
        if 'Archived News' in text or len(text) < 100:
            return ''
        return text

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
            content = self.extract_main_article_content(soup)
            
            # Extract case details
            charges = self._extract_charges(content)
            case_type = self._determine_case_type(title, content)
            # Remove extraction of defendant_name, location, disposition, description
            # Categorize charges
            charge_categories = self.categorizer.categorize_charges(charges, content)
            # Determine fraud info
            fraud_info = self._is_fraud_case(charge_categories, content)
            # Determine money laundering info
            laundering_info = self._is_money_laundering_case(content)
            # Attach fraud_info and laundering_info to CaseInfo (as attributes)
            case_info = CaseInfo(
                title=title,
                date=date,
                url=url,
                charges=charges,
                case_type=case_type,
                charge_categories=charge_categories
            )
            case_info.fraud_info = fraud_info
            case_info.money_laundering_flag = laundering_info["is_money_laundering"]
            case_info.money_laundering_evidence = laundering_info["evidence"]
            return case_info
            
        except Exception as e:
            logger.error(f"Error analyzing press release {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        # Try <article> h1 first
        article = soup.find('article')
        if article:
            h1 = article.find('h1')
            if h1:
                title = h1.get_text().strip()
                if title and title.lower() not in ['archived news', 'press release']:
                    return title
        # Fallback to global h1
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text().strip()
            if title and title.lower() not in ['archived news', 'press release']:
                return title
        # Fallback to <title> tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title and title.lower() not in ['archived news', 'press release']:
                return title
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
        """Extract charges from press release content, handling lists and more patterns."""
        charges = []
        # Improved charge patterns
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
            r'for (?:committing|conspiring to commit) ([^.]+)',
            r'on charges? of ([^.]+)',
        ]
        for pattern in charge_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Split on common delimiters and conjunctions
                for part in re.split(r',|;| and | or |\n|\u2022|- ', match):
                    charge = self._clean_charge_text(part)
                    if self._is_valid_charge(charge) and charge not in charges:
                        charges.append(charge)
        return charges

    def extract_indictment_number(self, content: str) -> str:
        """Extract indictment number or details if present."""
        match = re.search(r'(Indictment\s*(No\.|Number)?\s*[:#]?\s*[A-Za-z0-9\-]+)', content, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        return ""
    
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
    
    def get_current_date(self):
        """Get current date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")

    def extract_structured_info_gpt4o(self, text_or_soup, api_key: str = None) -> dict:
        """
        Use GPT-4o to extract structured case info from DOJ press release text with enhanced fraud detection.
        Accepts either raw text or a BeautifulSoup object.
        """
        if openai is None:
            raise ImportError("openai package is required for GPT-4o extraction. Please install with 'pip install openai'.")
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key must be provided via argument or OPENAI_API_KEY env var.")
        openai.api_key = api_key
        
        # If input is soup, extract main article content
        if isinstance(text_or_soup, BeautifulSoup):
            text = self.extract_main_article_content(text_or_soup)
        else:
            text = text_or_soup
        
        # Use FRAUD_KEYWORDS from constants.py for LLM prompt
        fraud_keywords = FRAUD_KEYWORDS
        
        prompt = f"""
You are a DOJ fraud legal researcher. Your primary task is to determine, with legal precision, whether the following DOJ press release describes a fraud case. Focus on legal standards, context, and the substance of the charges or conduct described. Ignore generic or irrelevant mentions of 'fraud' (e.g., in disclaimers, unrelated news, or boilerplate language). Only mark fraud_flag as true if the facts, charges, or context clearly indicate a fraud, scam, scheme, or deceptive practice as defined by law.

Extract the following fields as a JSON object (fraud_flag must be the first field):
- fraud_flag: Boolean, true if this is a fraud case, false otherwise (this is the key field)
- fraud_type: If fraud_flag is true, categorize the fraud type from: financial_fraud, healthcare_fraud, disaster_fraud, consumer_fraud, government_fraud, business_fraud, immigration_fraud, intellectual_property_fraud, general_fraud, or null if not fraud
- fraud_evidence: If fraud_flag is true, provide a brief snippet of evidence (string), otherwise null
- fraud_rationale: 1-2 sentences explaining why you classified this as fraud or not, referencing legal context or charge language
- title: The title of the press release
- date: The date of the press release
- charges: List all charges mentioned (array of strings)
- indictment_number: Indictment number if present, otherwise null
- charge_count: Number of charges found

FRAUD DETECTION GUIDELINES:
Use these keywords to identify fraud cases:
{json.dumps(fraud_keywords, indent=2)}

A case should be marked as fraud if it contains any of these keywords in a legally relevant context, or involves deceptive practices, schemes, or false representations as defined by law. Do not mark as fraud for generic mentions or unrelated uses of the word.

LOGICAL CONSISTENCY RULES:
- If you set fraud_type or fraud_evidence, you MUST set fraud_flag to true.
- If fraud_flag is false, fraud_type, fraud_evidence, and fraud_rationale must all be null.
- If fraud_type is not null or fraud_evidence is not null, fraud_flag must be true.
- If fraud_flag is false, fraud_type and fraud_evidence must be null.
- All fields must be logically consistent.

Return your answer as a JSON object with exactly these fields, in the order listed above.

Press Release:
{text}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a DOJ legal research assistant specializing in fraud case identification and legal data extraction. Always apply legal standards and context when determining fraud."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        # Try to parse the response as JSON
        content = response['choices'][0]['message']['content']
        
        # Handle markdown code blocks (```json ... ```)
        if content.startswith('```') and '```' in content[3:]:
            # Extract JSON from markdown code block
            start = content.find('```') + 3
            end = content.rfind('```')
            if start < end:
                json_content = content[start:end].strip()
                # Remove language identifier if present
                if json_content.startswith('json'):
                    json_content = json_content[4:].strip()
                content = json_content
        
        # After parsing the GPT-4o result, also run classic fraud detection for comparison
        try:
            result = json.loads(content)
            # Ensure all required fields are present
            required_fields = ['fraud_flag', 'fraud_type', 'fraud_evidence', 'fraud_rationale', 'title', 'date', 'charges', 'indictment_number', 'charge_count']
            for field in required_fields:
                if field not in result:
                    if field == 'charges':
                        result[field] = []
                    elif field == 'charge_count':
                        result[field] = len(result.get('charges', []))
                    elif field == 'fraud_flag':
                        result[field] = False
                    else:
                        result[field] = None
            # Ensure charges is always a list
            if not isinstance(result.get('charges'), list):
                result['charges'] = []
            # Update charge_count if not accurate
            result['charge_count'] = len(result['charges'])

            # --- Post-process for logical consistency ---
            if result.get('fraud_type') or result.get('fraud_evidence'):
                result['fraud_flag'] = True
            if not result.get('fraud_flag'):
                result['fraud_type'] = None
                result['fraud_evidence'] = None
                result['fraud_rationale'] = None
            # ---

            # --- Classic fraud detection cross-check ---
            charges = result.get('charges', [])
            charge_categories = self.categorizer.categorize_charges(charges, text)
            classic_fraud_info = self._is_fraud_case(charge_categories, text)
            result['classic_fraud_flag'] = bool(classic_fraud_info.is_fraud)
            result['classic_fraud_evidence'] = classic_fraud_info.evidence
            result['classic_fraud_categories'] = [cat.value for cat in charge_categories]
            # --- Money laundering detection ---
            laundering_info = self._is_money_laundering_case(text)
            result['money_laundering_flag'] = laundering_info["is_money_laundering"]
            result['money_laundering_evidence'] = laundering_info["evidence"]
            # ---
            return result
        except Exception as e:
            logger.error(f"Error parsing GPT-4o response: {e}")
            return {
                "fraud_flag": False,
                "fraud_type": None,
                "fraud_evidence": None,
                "fraud_rationale": None,
                "title": "Error parsing response",
                "date": None,
                "charges": [],
                "indictment_number": None,
                "charge_count": 0,
                "raw_response": content,
                "error": str(e)
            }

    def identify_fraud_and_rationale(self, content: str) -> dict:
        charges = self._extract_charges(content)
        charge_categories = self.categorizer.categorize_charges(charges, content)
        fraud_info = self._is_fraud_case(charge_categories, content)
        return {
            "is_fraud": fraud_info.is_fraud,
            "evidence": fraud_info.evidence,
            "charge_categories": [cat.value for cat in charge_categories]
        }