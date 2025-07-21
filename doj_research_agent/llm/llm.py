"""LLM extraction and analysis functions for DOJ press releases using LangChain."""

import os
import json
import logging
from typing import Union, Optional, Dict, Any, Type, TypeVar
from bs4 import BeautifulSoup
from ..core.constants import (
    LLM_PROMPT, FRAUD_KEYWORDS, INSTRUCTOR_SYSTEM_PROMPT, INSTRUCTOR_USER_PROMPT_TEMPLATE
)

# Import instructor and models
try:
    import instructor
    from .llm_models import CaseAnalysisResponse, SimpleCaseResponse, MoneyLaunderingResponse
    INSTRUCTOR_AVAILABLE = True
except ImportError:
    instructor = None
    CaseAnalysisResponse = None
    SimpleCaseResponse = None  
    MoneyLaunderingResponse = None
    INSTRUCTOR_AVAILABLE = False

T = TypeVar('T')

try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic  # Fixed import
    from langchain_community.llms import Ollama
    from langchain.schema import HumanMessage, SystemMessage
    from langchain.callbacks.manager import CallbackManager
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages different LLM providers through LangChain for flexible model switching."""
    
    def __init__(self, 
                 provider: str = "openai",
                 model: str = "gpt-4o",
                 api_key: Optional[str] = None,
                 temperature: float = 0.1,
                 max_tokens: int = 1500,
                 use_instructor: bool = True):
        """
        Initialize LLM manager with configurable provider and model.
        
        Args:
            provider: LLM provider ('openai', 'anthropic', 'ollama')
            model: Model name (e.g., 'gpt-4o', 'claude-3-sonnet', 'llama2')
            api_key: API key for the provider (if None, uses env vars)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            use_instructor: Whether to use instructor for structured output
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.use_instructor = use_instructor and INSTRUCTOR_AVAILABLE
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain packages are required. Install with: pip install langchain langchain-openai langchain-anthropic langchain-community")
        
        self.llm = self._initialize_llm(api_key)
        self.instructor_client = self._initialize_instructor_client() if self.use_instructor else None
    
    def _initialize_llm(self, api_key: Optional[str]):
        """Initialize the LLM based on provider."""
        if self.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key.")
            return ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                openai_api_key=api_key,
                max_tokens=self.max_tokens
            )
        
        elif self.provider == "anthropic":
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")  # Fixed: was using self.api_key
            if not api_key:
                raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key.")
            return ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                anthropic_api_key=api_key,
                max_tokens=self.max_tokens
            )
        
        elif self.provider == "ollama":
            return Ollama(
                model=self.model,
                temperature=self.temperature
            )
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Use 'openai', 'anthropic', or 'ollama'")
    
    def _initialize_instructor_client(self):
        """Initialize instructor client for structured output."""
        if not INSTRUCTOR_AVAILABLE:
            return None
            
        if self.provider == "openai":
            api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            try:
                import openai
                client = openai.OpenAI(api_key=api_key)
                return instructor.from_openai(client)
            except Exception as e:
                logger.warning(f"Failed to initialize instructor for OpenAI: {e}")
                return None
                
        elif self.provider == "anthropic":
            api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return None
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                return instructor.from_anthropic(client)
            except Exception as e:
                logger.warning(f"Failed to initialize instructor for Anthropic: {e}")
                return None
        
        return None
    
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using the configured LLM."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            if hasattr(response, 'content'):
                content = response.content
                return content if isinstance(content, str) else str(content)
            else:
                return str(response)
        except Exception as e:
            logger.error(f"Error generating response with {self.provider}: {e}")
            raise
    
    def generate_structured_response(self, response_model: Type[T], system_prompt: str, user_prompt: str) -> T:
        """Generate structured response using instructor."""
        if not self.use_instructor or not self.instructor_client:
            raise ValueError("Instructor not available. Initialize with use_instructor=True and ensure instructor package is installed.")
        
        try:
            response = self.instructor_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_model=response_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response
        except Exception as e:
            logger.error(f"Error generating structured response with {self.provider}: {e}")
            raise

# Default LLM instance for backwards compatibility
_default_llm_manager = None

def get_default_llm_manager() -> LLMManager:
    """Get or create default LLM manager."""
    global _default_llm_manager
    if _default_llm_manager is None:
        _default_llm_manager = LLMManager()
    return _default_llm_manager

def set_default_llm_config(provider: str = "openai", 
                          model: str = "gpt-4o", 
                          api_key: Optional[str] = None,
                          **kwargs):
    """Set default LLM configuration."""
    global _default_llm_manager
    _default_llm_manager = LLMManager(provider, model, api_key, **kwargs)

# --- LLM Extraction Functions ---
def extract_structured_info(text_or_soup: Union[str, BeautifulSoup], 
                           api_key: str = "",
                           provider: str = "openai",
                           model: str = "gpt-4o",
                           llm_manager: Optional[LLMManager] = None,
                           use_instructor: bool = True) -> dict:
    """
    Extract structured case info from DOJ press release text using instructor or LangChain.
    Supports multiple LLM providers for flexibility.
    
    Args:
        text_or_soup: Raw text or BeautifulSoup object
        api_key: API key for the LLM provider
        provider: LLM provider ('openai', 'anthropic', 'ollama')
        model: Model name
        llm_manager: Optional pre-configured LLMManager instance
        use_instructor: Whether to use instructor for structured output
    
    Returns:
        dict: Structured case information
    """
    # Use provided LLM manager or create new one
    if llm_manager is None:
        try:
            llm_manager = LLMManager(provider=provider, model=model, api_key=api_key, use_instructor=use_instructor)
        except Exception as e:
            # Fallback to legacy OpenAI implementation if LangChain fails
            logger.warning(f"LangChain initialization failed: {e}. Falling back to legacy OpenAI implementation.")
            return _legacy_extract_structured_info(text_or_soup, api_key)

    # If input is soup, extract main article content
    if isinstance(text_or_soup, BeautifulSoup):
        from .analyzer import CaseAnalyzer
        text = CaseAnalyzer().extract_main_article_content(text_or_soup)
    else:
        text = text_or_soup

    # Try instructor approach first if available
    if use_instructor and llm_manager.use_instructor and CaseAnalysisResponse:
        try:
            system_prompt = INSTRUCTOR_SYSTEM_PROMPT
            user_prompt = INSTRUCTOR_USER_PROMPT_TEMPLATE.format(
                FRAUD_KEYWORDS=json.dumps(FRAUD_KEYWORDS, indent=2),
                text=text
            )
            
            response = llm_manager.generate_structured_response(CaseAnalysisResponse, system_prompt, user_prompt)
            return response.dict()
            
        except Exception as e:
            logger.warning(f"Instructor approach failed: {e}. Falling back to text-based parsing.")
    
    # Fallback to text-based approach
    system_prompt = "You are a DOJ legal research assistant specializing in fraud case identification and legal data extraction. Always apply legal standards and context when determining fraud."
    user_prompt = LLM_PROMPT.format(text=text, FRAUD_KEYWORDS=json.dumps(FRAUD_KEYWORDS, indent=2))

    try:
        content = llm_manager.generate_response(system_prompt, user_prompt)
        return _parse_llm_response(content)
    except Exception as e:
        logger.error(f"Error with LangChain LLM: {e}")
        # Fallback to legacy implementation
        if OPENAI_AVAILABLE and provider == "openai":
            logger.info("Falling back to legacy OpenAI implementation")
            return _legacy_extract_structured_info(text_or_soup, api_key)
        else:
            return _create_error_response(content if 'content' in locals() else "", str(e))

def _parse_llm_response(content: str) -> dict:
    """Parse LLM response content and return structured data."""
    # Handle markdown code blocks (```json ... ```)
    if content.startswith('```') and '```' in content[3:]:
        start = content.find('```') + 3
        end = content.rfind('```')
        if start < end:
            json_content = content[start:end].strip()
            if json_content.startswith('json'):
                json_content = json_content[4:].strip()
            content = json_content

    try:
        result = json.loads(content)
        required_fields = ['fraud_flag', 'fraud_type', 'fraud_evidence', 'fraud_rationale', 'title', 'date', 'charges', 'indictment_number', 'charge_count']
        
        # Ensure all required fields exist with proper defaults
        for field in required_fields:
            if field not in result:
                if field == 'charges':
                    result[field] = []
                elif field == 'charge_count':
                    result[field] = 0
                elif field == 'fraud_flag':
                    result[field] = False
                else:
                    result[field] = None
        
        # Ensure charges is a list
        if not isinstance(result.get('charges'), list):
            result['charges'] = []
        
        # Update charge count based on charges list
        result['charge_count'] = len(result['charges'])
        
        # Set fraud flag based on fraud evidence
        if result.get('fraud_type') or result.get('fraud_evidence'):
            result['fraud_flag'] = True
        
        # Clear fraud-related fields if no fraud detected
        if not result.get('fraud_flag'):
            result['fraud_type'] = None
            result['fraud_evidence'] = None
            result['fraud_rationale'] = None
            
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from LLM response: {e}")
        return _create_error_response(content, f"JSON parsing error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error parsing LLM response: {e}")
        return _create_error_response(content, str(e))

def _create_error_response(content: str, error: str) -> dict:
    """Create standardized error response."""
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
        "error": error
    }

def _legacy_extract_structured_info(text_or_soup: Union[str, BeautifulSoup], api_key: str = "") -> dict:
    """Legacy OpenAI implementation for backwards compatibility."""
    if not OPENAI_AVAILABLE:
        raise ImportError("openai package is required for legacy extraction. Please install with 'pip install openai'.")
    
    api_key = api_key or os.getenv("OPENAI_API_KEY") or ""
    if not isinstance(api_key, str) or not api_key:
        raise ValueError("OpenAI API key must be provided via argument or OPENAI_API_KEY env var.")

    # If input is soup, extract main article content
    if isinstance(text_or_soup, BeautifulSoup):
        from .analyzer import CaseAnalyzer
        text = CaseAnalyzer().extract_main_article_content(text_or_soup)
    else:
        text = text_or_soup

    prompt = LLM_PROMPT.format(text=text, FRAUD_KEYWORDS=json.dumps(FRAUD_KEYWORDS, indent=2))

    # Handle both old and new OpenAI API versions
    try:
        # New OpenAI v1.x API
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a DOJ legal research assistant specializing in fraud case identification and legal data extraction. Always apply legal standards and context when determining fraud."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        content = response.choices[0].message.content or ""
        
    except (AttributeError, TypeError):
        # Legacy OpenAI v0.x API fallback
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a DOJ legal research assistant specializing in fraud case identification and legal data extraction. Always apply legal standards and context when determining fraud."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            content = response['choices'][0]['message']['content'] or ""
        except Exception as e:
            logger.error(f"Legacy OpenAI API failed: {e}")
            return _create_error_response("", f"Both OpenAI API versions failed: {str(e)}")
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return _create_error_response("", f"OpenAI API error: {str(e)}")
    
    return _parse_llm_response(content)