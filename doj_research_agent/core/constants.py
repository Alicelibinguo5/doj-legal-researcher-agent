LLM_PROMPT = """
You are a DOJ fraud legal researcher. Your primary task is to determine, with legal precision, whether the following DOJ press release describes a fraud case or a money laundering case. Focus on legal standards, context, and the substance of the charges or conduct described. Ignore generic or irrelevant mentions of 'fraud' or 'money laundering' (e.g., in disclaimers, unrelated news, or boilerplate language). Only mark fraud_flag or money_laundering_flag as true if the facts, charges, or context clearly indicate a fraud, scam, scheme, deceptive practice, or money laundering as defined by law.

Extract the following fields as a JSON object (fraud_flag must be the first field):
- fraud_flag: Boolean, true if this is a fraud case, false otherwise (this is the key field)
- fraud_type: If fraud_flag is true, categorize the fraud type from: financial_fraud, healthcare_fraud, disaster_fraud, consumer_fraud, government_fraud, business_fraud, immigration_fraud, intellectual_property_fraud, general_fraud, or null if not fraud
- fraud_evidence: If fraud_flag is true, provide a brief snippet of evidence (string), otherwise null
- money_laundering_flag: Boolean, true if this is a money laundering case, false otherwise
- money_laundering_evidence: If money_laundering_flag is true, provide a brief snippet of evidence (string), otherwise null
- Overlap_flag: if fraud_flag and money_laundering_flag are true -> True, else false
- indictment_number: Indictment number if present, otherwise null
- charge_count: Number of charges found

FRAUD DETECTION GUIDELINES:
Use these keywords to identify fraud cases:
{FRAUD_KEYWORDS}
MONEY LAUNDERING  GUIDELINES:
Use these keywords to identify money laundering cases:
{MONEY_LAUNDERING_KEYWORD}

A case should be marked as fraud/money laundering if it contains any of these keywords in a legally relevant context, or involves deceptive practices, schemes, or false representations as defined by law. 
 1. Do not mark as fraud or money laundering for generic mentions or unrelated uses of the word.
 2. When matching keywords, make sure whole word matches, not match of middle of characters

LOGICAL CONSISTENCY RULES:
- If you set fraud_type or fraud_evidence, you MUST set fraud_flag to true.
- If fraud_flag is false, fraud_type, fraud_evidence, and fraud_rationale must all be null.
- If fraud_type is not null or fraud_evidence is not null, fraud_flag must be true.
- If fraud_flag is false, fraud_type and fraud_evidence must be null.
- If money_laundering_flag is true, money_laundering_evidence must not be null.
- If money_laundering_flag is false, money_laundering_evidence must be null.
- All fields must be logically consistent.

Return your answer as a JSON object with exactly these fields, in the order listed above.

Press Release:
{text}
"""

FRAUD_KEYWORDS = {
    "general_fraud": ["fraud", "fraudulent", "defraud", "scheme", "scam", "deceive", "deception", "false", "fake", "counterfeit", "forgery", "phony", "bogus", "sham"],
    "financial_fraud": ["embezzlement", "money laundering", "ponzi scheme", "investment fraud", "securities fraud", "wire fraud", "mail fraud", "bank fraud", "credit card fraud", "identity theft", "mortgage fraud", "loan fraud", "insurance fraud", "tax evasion", "structuring", "shell company", "money mule"],
    "healthcare_fraud": ["medicare fraud", "medicaid fraud", "healthcare fraud", "medical fraud", "billing fraud", "upcoding", "unbundling", "kickback", "false billing", "phantom billing", "duplicate billing", "medical coding fraud", "pharmaceutical fraud", "prescription fraud"],
    "disaster_fraud": ["disaster fraud", "fema fraud", "relief fraud", "emergency fraud", "covid fraud", "pandemic fraud", "ppp fraud", "ppp loan fraud", "sba fraud", "small business fraud", "stimulus fraud"],
    "consumer_fraud": ["telemarketing fraud", "telemarketing scheme", "phone scam", "online fraud", "internet fraud", "cyber fraud", "digital fraud", "phishing", "phishing scheme", "bait and switch", "false advertising", "pyramid scheme"],
    "government_fraud": ["public corruption", "corruption", "bribery", "kickback", "official misconduct", "abuse of office", "false claims", "election fraud", "voter fraud", "ballot fraud"],
    "business_fraud": ["insider trading", "market manipulation", "price fixing", "bid rigging", "antitrust", "accounting fraud", "financial statement fraud", "corporate fraud", "business fraud"],
    "immigration_fraud": ["visa fraud", "citizenship fraud", "immigration fraud", "document fraud", "document forgery", "fake documents", "false statements", "perjury", "marriage fraud", "sham marriage"],
    "intellectual_property_fraud": ["counterfeiting", "piracy", "bootleg", "trademark infringement", "copyright infringement", "intellectual property theft", "fake goods", "counterfeit products"]
} 

MONEY_LAUNDERING_KEYWORD =  {
    "money_laundering": ["money laundering", "laundering", "laundered", "launder", "cleaning money", "proceeds of crime", "illicit funds", "placement", "layering", "integration", "smurfing", "structuring", "shell company", "front company", "offshore account", "hawala", "bulk cash", "wire transfer", "bank secrecy", "anti-money laundering", "aml", "financial crimes enforcement network", "finCEN", "suspicious activity report", "sar", "currency transaction report", "ctr", "unexplained wealth", "concealment of proceeds", "illegal proceeds", "dirty money", "clean money"]
    }

INSTRUCTOR_SYSTEM_PROMPT = "You are a DOJ legal research assistant specializing in fraud case identification and legal data extraction. Always apply legal standards and context when determining fraud."

INSTRUCTOR_USER_PROMPT_TEMPLATE = """
Use the provided press release to extract the required information.

Press Release:
{text}

FRAUD DETECTION GUIDELINES:
Use these keywords to identify fraud cases:
{fraud_keywords}

A case should be marked as fraud if it contains any of these keywords in a legally relevant context, or involves deceptive practices, schemes, or false representations as defined by law. Do not mark as fraud for generic mentions or unrelated uses of the word.
"""
