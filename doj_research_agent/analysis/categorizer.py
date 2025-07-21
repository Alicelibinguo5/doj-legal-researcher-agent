"""Charge categorization functionality."""

from typing import List, Dict, Set
from ..core.models import ChargeCategory
from ..core.utils import setup_logger
import openai

logger = setup_logger(__name__)


class ChargeCategorizer:
    """Categorizer for legal charges."""
    
    def __init__(self):
        """Initialize categorizer with keyword mappings."""
        self.category_keywords = self._build_category_keywords()
    
    def _build_category_keywords(self) -> Dict[ChargeCategory, Set[str]]:
        """Build keyword mappings for charge categories based on DOJ topics."""
        return {
            ChargeCategory.ANTITRUST: {"antitrust", "price fixing", "monopoly", "cartel"},
            ChargeCategory.ASSET_FORFEITURE: {"asset forfeiture", "seizure", "forfeiture"},
            ChargeCategory.BANKRUPTCY: {"bankruptcy", "insolvency", "bankrupt"},
            ChargeCategory.CIVIL_RIGHTS: {"civil rights", "discrimination", "hate crime", "voting rights", "police misconduct", "excessive force"},
            ChargeCategory.CONSUMER_PROTECTION: {
                "consumer protection", "deceptive practices", "scam", "scamming", "scammer", 
                "fraudulent marketing", "unfair business", "telemarketing fraud", "telemarketing scheme",
                "phone scam", "online fraud", "internet fraud", "digital fraud", "consumer fraud",
                "bait and switch", "false advertising", "misleading advertising", "deceptive advertising",
                "pyramid scheme", "multi-level marketing fraud", "work from home scam", "investment scam"
            },
            ChargeCategory.CYBERCRIME: {
                "cybercrime", "hacking", "phishing", "phishing scheme", "ransomware", "malware", 
                "data breach", "computer fraud", "cyber fraud", "digital fraud", "online fraud",
                "internet fraud", "computer hacking", "unauthorized access", "data theft", "identity theft",
                "identity fraud", "social security fraud", "credit card fraud", "bank fraud",
                "wire fraud", "mail fraud", "cyber attack", "cyber intrusion", "data breach",
                "breach", "hacked", "hacker", "cybercriminal", "cyber criminal"
            },
            ChargeCategory.DISASTER_FRAUD: {
                "disaster fraud", "fema fraud", "emergency relief fraud", "covid fraud", "pandemic fraud",
                "ppp fraud", "ppp loan fraud", "sba fraud", "small business fraud", "relief fraud",
                "emergency fraud", "disaster relief fraud", "hurricane fraud", "flood fraud",
                "wildfire fraud", "tornado fraud", "earthquake fraud", "emergency assistance fraud",
                "federal disaster fraud", "government relief fraud", "stimulus fraud", "covid relief fraud"
            },
            ChargeCategory.DRUGS: {"drug", "narcotics", "fentanyl", "cocaine", "heroin", "methamphetamine", "opioid", "marijuana", "controlled substance", "trafficking"},
            ChargeCategory.ENVIRONMENT: {"environment", "epa", "pollution", "hazardous waste", "clean air act", "clean water act"},
            ChargeCategory.FALSE_CLAIMS_ACT: {"false claims act", "false claim", "qui tam", "whistleblower"},
            ChargeCategory.FINANCIAL_FRAUD: {
                "financial fraud", "securities fraud", "investment fraud", "wire fraud", "mail fraud", 
                "bank fraud", "embezzlement", "embezzle", "embezzled", "embezzling", "money laundering", 
                "laundering", "laundered", "launder", "ponzi scheme", "ponzi", "pyramid scheme", 
                "insider trading", "insider information", "market manipulation", "accounting fraud",
                "financial statement fraud", "cooking the books", "corporate fraud", "business fraud",
                "commercial fraud", "mortgage fraud", "loan fraud", "credit fraud", "credit card fraud",
                "identity theft", "identity fraud", "social security fraud", "tax fraud", "tax evasion",
                "evasion", "evaded", "structuring", "money mule", "shell company", "shell corporation",
                "front company", "offshore fraud", "foreign bank fraud", "wire transfer fraud",
                "electronic fraud", "digital fraud", "online banking fraud", "check fraud", "check kiting",
                "kiting", "advance fee fraud", "advance fee scheme", "419 fraud", "nigerian prince scam",
                "lottery fraud", "lottery scam", "inheritance fraud", "inheritance scam"
            },
            ChargeCategory.FIREARMS_OFFENSES: {"firearms", "gun", "weapon", "illegal possession", "firearm trafficking"},
            ChargeCategory.FOREIGN_CORRUPTION: {"foreign corruption", "foreign bribery", "fcp act", "overseas bribery"},
            ChargeCategory.HEALTH_CARE_FRAUD: {
                "health care fraud", "medicare fraud", "medicaid fraud", "insurance fraud", "healthcare fraud",
                "medical fraud", "billing fraud", "upcoding", "unbundling", "kickback", "kickbacks",
                "false billing", "phantom billing", "duplicate billing", "medical billing fraud",
                "healthcare billing fraud", "medicare billing fraud", "medicaid billing fraud",
                "insurance billing fraud", "medical coding fraud", "upcoding fraud", "unbundling fraud",
                "medical kickback", "healthcare kickback", "pharmaceutical fraud", "drug fraud",
                "prescription fraud", "medical device fraud", "dme fraud", "durable medical equipment fraud",
                "home health fraud", "nursing home fraud", "hospice fraud", "ambulance fraud",
                "medical transportation fraud", "lab fraud", "laboratory fraud", "imaging fraud",
                "radiology fraud", "medical testing fraud", "clinical trial fraud", "research fraud",
                "medical research fraud", "healthcare research fraud", "medical device kickback",
                "pharmaceutical kickback", "drug kickback", "medical supply fraud", "medical equipment fraud"
            },
            ChargeCategory.IMMIGRATION: {
                "immigration", "visa fraud", "citizenship fraud", "illegal entry", "smuggling", "alien smuggling",
                "immigration fraud", "document fraud", "document forgery", "fake documents", "false documents",
                "false statements", "false declaration", "perjury", "immigration perjury", "visa perjury",
                "citizenship perjury", "marriage fraud", "sham marriage", "fake marriage", "green card fraud",
                "permanent resident fraud", "asylum fraud", "refugee fraud", "immigration document fraud",
                "passport fraud", "passport forgery", "fake passport", "birth certificate fraud",
                "birth certificate forgery", "fake birth certificate", "social security card fraud",
                "social security card forgery", "fake social security card", "driver license fraud",
                "driver license forgery", "fake driver license", "immigration identity fraud",
                "immigration identity theft", "immigration document forgery", "immigration document fraud",
                "immigration fraud scheme", "immigration fraud ring", "immigration fraud conspiracy",
                "immigration fraud conspiracy", "immigration fraud enterprise", "immigration fraud organization"
            },
            ChargeCategory.INTELLECTUAL_PROPERTY: {
                "intellectual property", "copyright", "trademark", "patent", "counterfeit", "counterfeiting",
                "counterfeited", "piracy", "pirated", "bootleg", "bootlegged", "trademark infringement",
                "copyright infringement", "patent infringement", "intellectual property theft",
                "ip theft", "trade secret theft", "trade secret", "industrial espionage", "corporate espionage",
                "knockoff", "knock off", "fake goods", "fake products", "counterfeit goods", "counterfeit products",
                "fake merchandise", "counterfeit merchandise", "fake brand", "counterfeit brand",
                "fake designer", "counterfeit designer", "fake luxury", "counterfeit luxury",
                "fake electronics", "counterfeit electronics", "fake pharmaceuticals", "counterfeit pharmaceuticals",
                "fake drugs", "counterfeit drugs", "fake medicine", "counterfeit medicine",
                "fake software", "counterfeit software", "fake music", "counterfeit music",
                "fake movies", "counterfeit movies", "fake dvds", "counterfeit dvds",
                "fake cds", "counterfeit cds", "fake clothing", "counterfeit clothing",
                "fake shoes", "counterfeit shoes", "fake handbags", "counterfeit handbags",
                "fake watches", "counterfeit watches", "fake jewelry", "counterfeit jewelry"
            },
            ChargeCategory.LABOR_EMPLOYMENT: {"labor", "employment", "wage theft", "workplace discrimination", "overtime violation"},
            ChargeCategory.NATIONAL_SECURITY: {"national security", "espionage", "terrorism", "classified information", "export control"},
            ChargeCategory.PUBLIC_CORRUPTION: {
                "public corruption", "bribery", "bribe", "kickback", "kickbacks", "official misconduct", 
                "abuse of office", "corruption", "corrupt", "government corruption", "political corruption",
                "elected official corruption", "public official corruption", "government official corruption",
                "political bribery", "campaign finance fraud", "campaign finance violation", "election fraud",
                "voter fraud", "ballot fraud", "voter intimidation", "election intimidation", "vote buying",
                "vote selling", "election bribery", "campaign bribery", "political kickback", "government kickback",
                "official bribery", "public bribery", "government bribery", "political corruption scheme",
                "government corruption scheme", "public corruption scheme", "corruption ring", "bribery ring",
                "kickback ring", "corruption conspiracy", "bribery conspiracy", "kickback conspiracy",
                "corruption enterprise", "bribery enterprise", "kickback enterprise", "corruption organization",
                "bribery organization", "kickback organization", "corruption racket", "bribery racket",
                "kickback racket", "corruption network", "bribery network", "kickback network"
            },
            ChargeCategory.TAX: {
                "tax", "tax evasion", "tax fraud", "irs", "internal revenue service", "tax evasion",
                "evasion", "evaded", "tax avoidance", "tax avoidance scheme", "tax shelter", "tax shelter fraud",
                "offshore tax evasion", "offshore tax fraud", "foreign tax evasion", "foreign tax fraud",
                "tax haven", "tax haven fraud", "tax haven evasion", "tax haven scheme", "tax haven conspiracy",
                "tax fraud scheme", "tax evasion scheme", "tax fraud conspiracy", "tax evasion conspiracy",
                "tax fraud ring", "tax evasion ring", "tax fraud enterprise", "tax evasion enterprise",
                "tax fraud organization", "tax evasion organization", "tax fraud network", "tax evasion network",
                "tax fraud racket", "tax evasion racket", "tax fraud operation", "tax evasion operation",
                "false tax return", "false tax returns", "filing false tax return", "filing false tax returns",
                "false tax filing", "false tax filings", "tax return fraud", "tax filing fraud",
                "tax document fraud", "tax document forgery", "fake tax documents", "false tax documents",
                "tax identity theft", "tax identity fraud", "stolen identity refund fraud", "sirf",
                "identity theft refund fraud", "itrf", "tax refund fraud", "false tax refund",
                "fraudulent tax refund", "fake tax refund", "tax refund scheme", "tax refund conspiracy"
            },
            ChargeCategory.VIOLENT_CRIME: {"violent crime", "murder", "homicide", "assault", "robbery", "kidnapping", "arson", "carjacking", "gang", "firearms", "domestic violence"},
            ChargeCategory.VOTING_ELECTIONS: {
                "voting", "election", "election fraud", "ballot", "voter intimidation", "voter fraud",
                "ballot fraud", "election fraud", "voting fraud", "vote fraud", "vote buying", "vote selling",
                "election bribery", "voter bribery", "ballot bribery", "election corruption", "voting corruption",
                "election scheme", "voting scheme", "ballot scheme", "election conspiracy", "voting conspiracy",
                "ballot conspiracy", "election racket", "voting racket", "ballot racket", "election intimidation",
                "voter intimidation", "ballot intimidation", "election threat", "voter threat", "ballot threat",
                "election coercion", "voter coercion", "ballot coercion", "election manipulation", "voting manipulation",
                "ballot manipulation", "election tampering", "voting tampering", "ballot tampering", "election rigging",
                "voting rigging", "ballot rigging", "election fixing", "voting fixing", "ballot fixing"
            },
            ChargeCategory.OTHER: set()
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
    
    def categorize_charge(self, charge: str, content: str = "") -> List[ChargeCategory]:
        """
        Categorize a single charge string. Returns a list of ChargeCategory.
        """
        return self.categorize_charges([charge], content)
    
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
        """
        descriptions = {
            ChargeCategory.ANTITRUST: "Antitrust violations including price fixing, monopoly, and cartel activities.",
            ChargeCategory.ASSET_FORFEITURE: "Asset forfeiture and seizure cases.",
            ChargeCategory.BANKRUPTCY: "Bankruptcy and insolvency-related offenses.",
            ChargeCategory.CIVIL_RIGHTS: "Civil rights violations including discrimination, hate crimes, and police misconduct.",
            ChargeCategory.CONSUMER_PROTECTION: "Consumer protection violations, scams, and deceptive practices.",
            ChargeCategory.CYBERCRIME: "Cybercrime including hacking, phishing, ransomware, and data breaches.",
            ChargeCategory.DISASTER_FRAUD: "Fraud related to disasters, emergency relief, and FEMA.",
            ChargeCategory.DRUGS: "Drug-related offenses including trafficking, possession, and manufacturing.",
            ChargeCategory.ENVIRONMENT: "Environmental crimes including pollution and hazardous waste.",
            ChargeCategory.FALSE_CLAIMS_ACT: "False Claims Act violations and whistleblower cases.",
            ChargeCategory.FINANCIAL_FRAUD: "Financial fraud including securities, investment, and bank fraud.",
            ChargeCategory.FIREARMS_OFFENSES: "Firearms and weapons offenses.",
            ChargeCategory.FOREIGN_CORRUPTION: "Foreign corruption and overseas bribery cases.",
            ChargeCategory.HEALTH_CARE_FRAUD: "Health care fraud including Medicare and Medicaid fraud.",
            ChargeCategory.IMMIGRATION: "Immigration-related offenses including visa and citizenship fraud.",
            ChargeCategory.INTELLECTUAL_PROPERTY: "Intellectual property crimes including copyright and trademark violations.",
            ChargeCategory.LABOR_EMPLOYMENT: "Labor and employment violations including wage theft and workplace discrimination.",
            ChargeCategory.NATIONAL_SECURITY: "National security offenses including terrorism and espionage.",
            ChargeCategory.PUBLIC_CORRUPTION: "Public corruption including bribery and official misconduct.",
            ChargeCategory.TAX: "Tax-related crimes including tax evasion and fraud.",
            ChargeCategory.VIOLENT_CRIME: "Violent crimes including murder, assault, robbery, and gang activity.",
            ChargeCategory.VOTING_ELECTIONS: "Voting and election-related offenses including election fraud.",
            ChargeCategory.OTHER: "Other charges not fitting into main categories."
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