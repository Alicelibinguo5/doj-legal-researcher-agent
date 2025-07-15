"""Charge categorization functionality."""

from typing import List, Dict, Set
from .models import ChargeCategory
from .utils import setup_logger

logger = setup_logger(__name__)


class ChargeCategorizer:
    """Categorizer for legal charges."""
    
    def __init__(self):
        """Initialize categorizer with keyword mappings."""
        self.category_keywords = self._build_category_keywords()
    
    def _build_category_keywords(self) -> Dict[ChargeCategory, Set[str]]:
        """Build keyword mappings for charge categories."""
        return {
            ChargeCategory.FINANCIAL_CRIMES: {
                'fraud', 'embezzlement', 'money laundering', 'tax evasion',
                'securities fraud', 'wire fraud', 'mail fraud', 'bank fraud',
                'investment fraud', 'ponzi scheme', 'insider trading',
                'check fraud', 'credit card fraud', 'mortgage fraud',
                'healthcare fraud', 'medicare fraud', 'insurance fraud',
                'bankruptcy fraud', 'procurement fraud', 'bribery',
                'kickback', 'corruption', 'tax fraud', 'identity theft',
                'forgery', 'counterfeiting', 'racketeering', 'rico',
                'financial institution fraud', 'commodities fraud'
            },
            
            ChargeCategory.DRUG_CRIMES: {
                'drug trafficking', 'drug distribution', 'drug possession',
                'narcotics', 'controlled substance', 'fentanyl', 'cocaine',
                'heroin', 'methamphetamine', 'opioid', 'marijuana',
                'prescription drugs', 'drug conspiracy', 'drug manufacturing',
                'drug importation', 'drug smuggling', 'synthetic drugs',
                'drug dealing', 'drug sales', 'drug transportation',
                'drug cultivation', 'drug laboratory', 'drug precursor'
            },
            
            ChargeCategory.VIOLENT_CRIMES: {
                'murder', 'homicide', 'manslaughter', 'assault', 'battery',
                'robbery', 'armed robbery', 'kidnapping', 'extortion',
                'racketeering', 'rico', 'gang', 'organized crime',
                'weapons charges', 'firearms', 'gun violence',
                'domestic violence', 'sexual assault', 'rape',
                'child abuse', 'elder abuse', 'human trafficking',
                'sex trafficking', 'terrorism', 'bomb threat',
                'arson', 'carjacking', 'hate crime'
            },
            
            ChargeCategory.CYBERCRIME: {
                'computer fraud', 'hacking', 'cybersecurity', 'data breach',
                'identity theft', 'phishing', 'ransomware', 'cyber attack',
                'computer intrusion', 'network intrusion', 'malware',
                'ddos', 'denial of service', 'cyber espionage',
                'computer access', 'unauthorized access', 'cyber stalking',
                'online fraud', 'internet fraud', 'email fraud',
                'social engineering', 'cryptocurrency fraud', 'digital fraud'
            },
            
            ChargeCategory.PUBLIC_CORRUPTION: {
                'bribery', 'corruption', 'public official', 'government contract',
                'kickback', 'conflict of interest', 'abuse of office',
                'official misconduct', 'honest services fraud',
                'public corruption', 'political corruption', 'election fraud',
                'campaign finance', 'lobbying violation', 'ethics violation',
                'gratuity', 'quid pro quo', 'influence peddling',
                'nepotism', 'cronyism', 'misuse of public funds'
            },
            
            ChargeCategory.IMMIGRATION: {
                'immigration fraud', 'human trafficking', 'smuggling',
                'visa fraud', 'citizenship fraud', 'document fraud',
                'illegal entry', 'illegal reentry', 'harboring aliens',
                'transporting aliens', 'marriage fraud', 'asylum fraud',
                'passport fraud', 'border crossing', 'human smuggling',
                'alien smuggling', 'immigration violation'
            },
            
            ChargeCategory.CIVIL_RIGHTS: {
                'civil rights violation', 'hate crime', 'discrimination',
                'police misconduct', 'excessive force', 'color of law',
                'deprivation of rights', 'voting rights', 'housing discrimination',
                'employment discrimination', 'disability discrimination',
                'racial discrimination', 'religious discrimination',
                'gender discrimination', 'age discrimination',
                'constitutional violation', 'section 1983'
            }
        }
    
    def categorize_charges(self, charges: List[str], content: str = "") -> List[ChargeCategory]:
        """
        Categorize charges based on keywords and content.
        
        Args:
            charges: List of charge descriptions
            content: Additional content to analyze
            
        Returns:
            List of charge categories
        """
        categories = set()
        
        # Combine charges and content for analysis
        text_to_analyze = " ".join(charges + [content]).lower()
        
        # Check each category for keyword matches
        for category, keywords in self.category_keywords.items():
            if self._has_keyword_match(text_to_analyze, keywords):
                categories.add(category)
        
        # Return as list, defaulting to OTHER if no matches
        result = list(categories) if categories else [ChargeCategory.OTHER]
        
        logger.debug(f"Categorized charges: {[cat.value for cat in result]}")
        return result
    
    def _has_keyword_match(self, text: str, keywords: Set[str]) -> bool:
        """
        Check if text contains any of the keywords.
        
        Args:
            text: Text to search
            keywords: Set of keywords to look for
            
        Returns:
            True if any keyword is found
        """
        for keyword in keywords:
            if keyword in text:
                return True
        return False
    
    def get_category_description(self, category: ChargeCategory) -> str:
        """
        Get a description of a charge category.
        
        Args:
            category: Charge category
            
        Returns:
            Description of the category
        """
        descriptions = {
            ChargeCategory.FINANCIAL_CRIMES: "Financial crimes including fraud, embezzlement, money laundering, and tax evasion",
            ChargeCategory.DRUG_CRIMES: "Drug-related offenses including trafficking, distribution, and possession",
            ChargeCategory.VIOLENT_CRIMES: "Violent crimes including murder, assault, robbery, and weapons charges",
            ChargeCategory.CYBERCRIME: "Computer and internet-related crimes including hacking, fraud, and data breaches",
            ChargeCategory.PUBLIC_CORRUPTION: "Public corruption including bribery, kickbacks, and abuse of office",
            ChargeCategory.IMMIGRATION: "Immigration-related offenses including fraud, smuggling, and violations",
            ChargeCategory.CIVIL_RIGHTS: "Civil rights violations including discrimination and police misconduct",
            ChargeCategory.OTHER: "Other charges not fitting into main categories"
        }
        return descriptions.get(category, "Unknown category")
    
    def get_all_categories(self) -> List[ChargeCategory]:
        """Get all available charge categories."""
        return list(ChargeCategory)
    
    def add_keywords_to_category(self, category: ChargeCategory, keywords: Set[str]):
        """
        Add keywords to a category.
        
        Args:
            category: Category to add keywords to
            keywords: Set of keywords to add
        """
        if category in self.category_keywords:
            self.category_keywords[category].update(keywords)
        else:
            self.category_keywords[category] = keywords
        
        logger.info(f"Added {len(keywords)} keywords to category {category.value}")
    
    def remove_keywords_from_category(self, category: ChargeCategory, keywords: Set[str]):
        """
        Remove keywords from a category.
        
        Args:
            category: Category to remove keywords from
            keywords: Set of keywords to remove
        """
        if category in self.category_keywords:
            self.category_keywords[category] -= keywords
            logger.info(f"Removed {len(keywords)} keywords from category {category.value}")
    
    def get_keywords_for_category(self, category: ChargeCategory) -> Set[str]:
        """
        Get keywords for a specific category.
        
        Args:
            category: Category to get keywords for
            
        Returns:
            Set of keywords for the category
        """
        return self.category_keywords.get(category, set())